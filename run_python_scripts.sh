#!/bin/bash
# Run the Python scripts that work with the data stored in this repository.
# Each script runs from its own folder, with a non-interactive plotting backend.
set -e
export MPLBACKEND=Agg
ROOT="$(cd "$(dirname "$0")" && pwd)"

SCRIPTS=(
  demonstration-feature-selection/src/main_demons_selector.py
  demonstration-feature-selection/src/main_feature_selector.py
  demonstration-feature-selection/src/viewers/viewDemo2x3dof.py
  demonstration-feature-selection/src/viewers/viewDemo3dof.py
  demonstration-feature-selection/src/viewers/viewSingleFeature.py
  demonstration-feature-selection/src/alternatives/main_dtw_mds_dbscan.py
  demonstration-feature-selection/src/alternatives/main_dtw_mds_norm.py
  friction-gravity-compensation/friction/accel_stability.py
  friction-gravity-compensation/friction/torque_vs_vel.py
  friction-gravity-compensation/friction/vel_stability.py
  guided-motor-primitives/src/roman14_cleanPlot.py
  guided-motor-primitives/src/roman14_paintPlot.py
  simulated-CGDA/fitness/fitnessplot.py
  simulated-CGDA/generalization/generalization_old_visual.py
  simulated-CGDA/recognition/dtw_visual.py
  simulated-CGDA/recognition/recognition_test1.py
  simulated-CGDA/recognition/recognition_test2.py
  "simulated-CGDA/recognition/traj_comparison 2d.py"
)
# friction/vel_vs_time.py also works, but it appends to curves/leftArm/joint22/torques22.txt

for script in "${SCRIPTS[@]}"; do
  echo "== $script"
  (cd "$ROOT/$(dirname "$script")" && python "$(basename "$script")" > /dev/null)
done
echo "All ${#SCRIPTS[@]} scripts ran successfully."
