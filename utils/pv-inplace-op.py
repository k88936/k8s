#!/usr/bin/env python3
"""
Remove nodeAffinity from Longhorn PersistentVolume

This script safely removes nodeAffinity restrictions from a PV by:
1. Backing up the original PV configuration
2. Changing reclaim policy to Retain (prevents accidental data loss)
3. Deleting the old PV
4. Recreating it without nodeAffinity

Usage:
    python3 remove-pv-nodeaffinity.py <pv-name>

Example:
    python3 remove-pv-nodeaffinity.py pvc-f87681f5-7021-4f84-b966-7caa5254de7f
"""

import sys
import json
import subprocess
import time
from datetime import datetime
from pathlib import Path


def run_kubectl(args, capture_output=True, check=True):
    """Run kubectl command and return result"""
    cmd = ["kubectl"] + args
    result = subprocess.run(
        cmd,
        capture_output=capture_output,
        text=True,
        check=False
    )
    
    if check and result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    
    return result


def get_pv(pv_name):
    """Get PV configuration as dict"""
    result = run_kubectl(["get", "pv", pv_name, "-o", "json"])
    return json.loads(result.stdout)


def backup_pv(pv_name, pv_data):
    """Backup PV configuration to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"pv-{pv_name}-backup-{timestamp}.yaml"
    
    result = run_kubectl(["get", "pv", pv_name, "-o", "yaml"])
    
    with open(backup_file, "w") as f:
        f.write(result.stdout)
    
    print(f"✅ Backup saved to: {backup_file}")
    return backup_file


def change_reclaim_policy(pv_name, policy="Retain"):
    """Change PV reclaim policy"""
    print(f"🔧 Changing reclaim policy to {policy}...")
    
    patch = {
        "spec": {
            "persistentVolumeReclaimPolicy": policy
        }
    }
    
    result = run_kubectl([
        "patch", "pv", pv_name,
        "--type=merge",
        "-p", json.dumps(patch)
    ])
    
    print(f"✅ Reclaim policy changed to {policy}")


def check_volume_state(pv_name):
    """Check if Longhorn volume is detached"""
    result = run_kubectl([
        "get", "volumes.longhorn.io", "-n", "longhorn-system",
        pv_name, "-o", "jsonpath={.status.state}"
    ], check=False)
    
    if result.returncode == 0:
        state = result.stdout.strip()
        print(f"📊 Longhorn volume state: {state}")
        return state
    return None


def create_fixed_pv_manifest(pv_data):
    """Create PV manifest without nodeAffinity"""
    
    # Start with clean spec
    new_pv = {
        "apiVersion": "v1",
        "kind": "PersistentVolume",
        "metadata": {
            "name": pv_data["metadata"]["name"],
            "annotations": {
                "pv.kubernetes.io/provisioned-by": pv_data["metadata"]["annotations"].get(
                    "pv.kubernetes.io/provisioned-by", "driver.longhorn.io"
                )
            }
        },
        "spec": {
            "accessModes": pv_data["spec"]["accessModes"],
            "capacity": pv_data["spec"]["capacity"],
            "claimRef": pv_data["spec"]["claimRef"],
            "csi": pv_data["spec"]["csi"],
            "persistentVolumeReclaimPolicy": pv_data["spec"]["persistentVolumeReclaimPolicy"],
            "storageClassName": pv_data["spec"]["storageClassName"],
            "volumeMode": pv_data["spec"]["volumeMode"]
        }
    }
    
    # Explicitly NOT including nodeAffinity
    
    return new_pv


def unbind_pv(pv_name):
    """Remove claimRef to unbind PV from PVC (prevents PVC deletion)"""
    print(f"🔓 Unbinding PV from PVC...")
    
    patch = {
        "spec": {
            "claimRef": None
        }
    }
    
    run_kubectl([
        "patch", "pv", pv_name,
        "--type=merge",
        "-p", json.dumps(patch)
    ])
    
    print("✅ PV unbound from PVC")
    time.sleep(2)


def delete_pv(pv_name):
    """Delete PV"""
    print(f"🗑️  Deleting PV {pv_name}...")
    
    # Delete without waiting
    run_kubectl(["delete", "pv", pv_name, "--wait=false"], check=False)
    
    # Remove finalizers
    print("🔧 Removing finalizers...")
    patch = {"metadata": {"finalizers": None}}
    run_kubectl([
        "patch", "pv", pv_name,
        "--type=merge",
        "-p", json.dumps(patch)
    ], check=False)
    
    # Wait for deletion
    print("⏳ Waiting for deletion...")
    time.sleep(3)
    
    # Verify deletion
    result = run_kubectl(["get", "pv", pv_name], check=False)
    if result.returncode != 0:
        print("✅ PV deleted successfully")
    else:
        print("⚠️  PV still exists, continuing anyway...")


def create_pv(pv_manifest, pv_name):
    """Create new PV from manifest"""
    print(f"📝 Creating new PV without nodeAffinity...")
    
    manifest_file = f"pv-{pv_name}-fixed.yaml"
    
    # Write manifest to file
    with open(manifest_file, "w") as f:
        json.dump(pv_manifest, f, indent=2)
    
    # Apply manifest
    result = run_kubectl(["apply", "-f", manifest_file])
    
    print(f"✅ New PV created (manifest: {manifest_file})")
    return manifest_file


def verify_pv(pv_name):
    """Verify PV has no nodeAffinity"""
    print(f"🔍 Verifying PV {pv_name}...")
    
    pv_data = get_pv(pv_name)
    
    # Check for nodeAffinity
    has_affinity = "nodeAffinity" in pv_data.get("spec", {})
    
    if has_affinity:
        print("❌ WARNING: PV still has nodeAffinity!")
        print(json.dumps(pv_data["spec"]["nodeAffinity"], indent=2))
        return False
    else:
        print("✅ SUCCESS: No nodeAffinity restriction")
    
    # Check PV status
    status = pv_data.get("status", {}).get("phase")
    print(f"📊 PV Status: {status}")
    
    # Check claim ref
    claim_ref = pv_data.get("spec", {}).get("claimRef", {})
    pvc_name = claim_ref.get("name")
    pvc_namespace = claim_ref.get("namespace")
    
    if pvc_name and pvc_namespace:
        print(f"📎 Bound to: {pvc_namespace}/{pvc_name}")
    
    return not has_affinity


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    
    pv_name = sys.argv[1]
    
    print("=" * 80)
    print(f"Remove nodeAffinity from PV: {pv_name}")
    print("=" * 80)
    print()
    
    try:
        # Step 1: Get current PV
        print("📥 Step 1: Fetching PV configuration...")
        pv_data = get_pv(pv_name)
        
        # Step 2: Backup
        print("💾 Step 2: Creating backup...")
        backup_file = backup_pv(pv_name, pv_data)
        print()
        
        # Step 3: Check volume state
        print("🔍 Step 3: Checking Longhorn volume state...")
        state = check_volume_state(pv_name)
        if state == "attached":
            print("⚠️  WARNING: Volume is attached to a pod!")
            print("It's safer to proceed when volume is detached.")
            response = input("Continue anyway? (yes/no): ")
            if response.lower() != "yes":
                print("❌ Aborted by user")
                sys.exit(1)
        print()
        
        # Step 4: Change reclaim policy to Retain
        print("🛡️  Step 4: Changing reclaim policy to Retain...")
        original_policy = pv_data["spec"]["persistentVolumeReclaimPolicy"]
        print(f"Original policy: {original_policy}")
        change_reclaim_policy(pv_name, "Retain")
        print()
        
        # Step 5: Verify PVC exists and save its info
        print("🔍 Step 5: Verifying PVC exists...")
        pvc_name = pv_data["spec"]["claimRef"]["name"]
        pvc_namespace = pv_data["spec"]["claimRef"]["namespace"]
        
        result = run_kubectl(["get", "pvc", pvc_name, "-n", pvc_namespace], check=False)
        if result.returncode != 0:
            print(f"❌ ERROR: PVC {pvc_namespace}/{pvc_name} not found!")
            print("Cannot proceed safely. Aborting.")
            sys.exit(1)
        print(f"✅ PVC exists: {pvc_namespace}/{pvc_name}")
        print()
        
        # Step 6: Unbind PV from PVC (CRITICAL: prevents PVC deletion)
        print("🔓 Step 6: Unbinding PV from PVC (prevents PVC deletion)...")
        unbind_pv(pv_name)
        print()
        
        # Step 7: Verify PVC still exists after unbinding
        print("🔍 Step 7: Verifying PVC still exists after unbinding...")
        result = run_kubectl(["get", "pvc", pvc_name, "-n", pvc_namespace], check=False)
        if result.returncode != 0:
            print(f"❌ ERROR: PVC was deleted! This should not happen!")
            sys.exit(1)
        
        # Check PVC status
        pvc_status = run_kubectl([
            "get", "pvc", pvc_name, "-n", pvc_namespace,
            "-o", "jsonpath={.status.phase}"
        ]).stdout.strip()
        print(f"✅ PVC status: {pvc_status}")
        print()
        
        # Step 8: Create fixed manifest
        print("📝 Step 8: Creating fixed PV manifest (without nodeAffinity)...")
        fixed_manifest = create_fixed_pv_manifest(pv_data)
        # Restore original reclaim policy in the new manifest
        fixed_manifest["spec"]["persistentVolumeReclaimPolicy"] = original_policy
        print("✅ Manifest created")
        print()
        
        # Step 9: Delete old PV
        print("🗑️  Step 9: Deleting old PV (PVC is protected)...")
        delete_pv(pv_name)
        print()
        
        # Step 10: Verify PVC still exists before creating new PV
        print("🔍 Step 10: Final PVC verification before recreating PV...")
        result = run_kubectl(["get", "pvc", pvc_name, "-n", pvc_namespace], check=False)
        if result.returncode != 0:
            print(f"❌ CRITICAL: PVC {pvc_namespace}/{pvc_name} was deleted!")
            print("Cannot proceed. You will need to recreate the PVC manually.")
            sys.exit(1)
        print(f"✅ PVC still exists")
        print()
        
        # Step 11: Create new PV
        print("📦 Step 11: Creating new PV...")
        manifest_file = create_pv(fixed_manifest, pv_name)
        print()
        
        # Step 12: Wait for PVC to rebind
        print("⏳ Step 12: Waiting for PVC to rebind to new PV...")
        time.sleep(3)
        
        pvc_status = run_kubectl([
            "get", "pvc", pvc_name, "-n", pvc_namespace,
            "-o", "jsonpath={.status.phase}"
        ]).stdout.strip()
        print(f"PVC status: {pvc_status}")
        
        if pvc_status != "Bound":
            print("⚠️  WARNING: PVC is not Bound yet. It may take a moment...")
        print()
        
        # Step 13: Verify
        print("✔️  Step 13: Verifying...")
        success = verify_pv(pv_name)
        print()
        
        # Step 14: Final PVC check
        print("✔️  Step 14: Final PVC verification...")
        result = run_kubectl(["get", "pvc", pvc_name, "-n", pvc_namespace])
        print(f"✅ PVC {pvc_namespace}/{pvc_name} is intact")
        print()
        
        if success:
            print("=" * 80)
            print("🎉 SUCCESS! NodeAffinity removed successfully!")
            print("=" * 80)
            print()
            print(f"📄 Backup file: {backup_file}")
            print(f"📄 New manifest: {manifest_file}")
            print()
            print("Next steps:")
            print(f"  - Verify PVC is still bound: kubectl get pvc -A | grep {pv_name}")
            print(f"  - Check Longhorn volume: kubectl get volumes.longhorn.io -n longhorn-system {pv_name}")
            print(f"  - Test pod scheduling with this PVC")
        else:
            print("=" * 80)
            print("⚠️  WARNING: Verification failed!")
            print("=" * 80)
            print(f"Check the backup file: {backup_file}")
    
    except KeyboardInterrupt:
        print("\n\n❌ Aborted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()