#!/bin/bash
#SBATCH --job-name=grp04_cpu_train_modelo_final
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=4
#SBATCH --mem=12G
#SBATCH --time=04:00:00
#SBATCH --output=/data/models/grp04/logs/grp04_cpu_train_modelo_final_%j.out

set -e

GROUP_ID="grp04"
WORKSPACE="/srv/data-platform/grp04/workspace"
OUTPUTS="/data/models/grp04"
IMAGE="/opt/apptainer-images/tensorflow_ngc_24.04_tf2_py3_mlcv.sif"
SCRIPT_NAME="train_modelo_final.py"

echo "================================="
echo " Trabajo CPU enviado por Slurm"
echo " Grupo: ${GROUP_ID}"
echo " Host: $(hostname)"
echo " Job ID: ${SLURM_JOB_ID}"
echo " Script: ${SCRIPT_NAME}"
echo " Workspace: ${WORKSPACE}"
echo " Outputs: ${OUTPUTS}"
echo " Imagen: ${IMAGE}"
echo " Partición: cpu"
echo " CPUs asignadas: ${SLURM_CPUS_PER_TASK}"
echo " Memoria solicitada: 12G"
echo " Tiempo máximo: 04:00:00"
echo " Inicio: $(date)"
echo "================================="

export OMP_NUM_THREADS="1"            # antes: "${SLURM_CPUS_PER_TASK}"
export OPENBLAS_NUM_THREADS="1"       # antes: "${SLURM_CPUS_PER_TASK}"
export MKL_NUM_THREADS="1"            # antes: "${SLURM_CPUS_PER_TASK}"
export NUMEXPR_NUM_THREADS="1"        # antes: "${SLURM_CPUS_PER_TASK}"
export VECLIB_MAXIMUM_THREADS="1"     # antes: "${SLURM_CPUS_PER_TASK}"
export LOKY_MAX_CPU_COUNT="${SLURM_CPUS_PER_TASK}"

export APPTAINERENV_OMP_NUM_THREADS="1"         # antes: "${SLURM_CPUS_PER_TASK}"
export APPTAINERENV_OPENBLAS_NUM_THREADS="1"    # antes: "${SLURM_CPUS_PER_TASK}"
export APPTAINERENV_MKL_NUM_THREADS="1"         # antes: "${SLURM_CPUS_PER_TASK}"
export APPTAINERENV_NUMEXPR_NUM_THREADS="1"     # antes: "${SLURM_CPUS_PER_TASK}"
export APPTAINERENV_VECLIB_MAXIMUM_THREADS="1"  # antes: "${SLURM_CPUS_PER_TASK}"
export APPTAINERENV_LOKY_MAX_CPU_COUNT="${SLURM_CPUS_PER_TASK}"


echo "Límites de paralelismo CPU:"
echo "OMP_NUM_THREADS=${OMP_NUM_THREADS}"
echo "OPENBLAS_NUM_THREADS=${OPENBLAS_NUM_THREADS}"
echo "MKL_NUM_THREADS=${MKL_NUM_THREADS}"
echo "NUMEXPR_NUM_THREADS=${NUMEXPR_NUM_THREADS}"
echo "LOKY_MAX_CPU_COUNT=${LOKY_MAX_CPU_COUNT}"
echo "================================="

#apptainer exec \
#  --bind "${WORKSPACE}:/work" \
#  --bind "${OUTPUTS}:/outputs" \
#  "${IMAGE}" \
#  python "/work/train/${SCRIPT_NAME}"


echo "CPU affinity dentro del batch antes de srun:"
taskset -pc $$ || true

srun --ntasks=1 --cpus-per-task="${SLURM_CPUS_PER_TASK}" --cpu-bind=verbose,cores   apptainer exec     --bind "${WORKSPACE}:/work"     --bind "${OUTPUTS}:/outputs"     "${IMAGE}"     python "/work/train/${SCRIPT_NAME}"

echo "================================="
echo " Trabajo CPU finalizado"
echo " Fin: $(date)"
echo " Resultados en: ${OUTPUTS}"
echo "================================="
