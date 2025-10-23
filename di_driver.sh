#!/bin/sh
 
# === User configuration ===
YEAR=2024
DATAPATH='/scratch4/BMC/wrfruc/llin/2025-zrtrr2/240601_misc/20241213-ncdiag-rrfs-full/rrfs/na/prod'

# please comment out one of them: 1) True, for the entire domain; 2) or a prescribed rectangular sub-domain
#DOMAIN_STR="True" 
DOMAIN_STR="(anl_latitude>15) & (anl_latitude<43) & (anl_longitude>267) & (anl_longitude<282)"

# === Setup output directories ===
mkdir -p figures logs pickle

# === Cycles to process ===
for MM in 09; do
  
  # for DD in 27 28; do
  for DD in 27; do
	  
    #for HH in {00..23}; do
    for HH in 06; do
	        
      CYCLE="${YEAR}${MM}${DD}${HH}"
	  JOBNAME="pygsi_${CYCLE}"
	  LOGFILE="logs/${JOBNAME}.log"
	  RRFS_PATH="${DATAPATH}/rrfs.${YEAR}${MM}${DD}"

	  echo "=== Processing cycle ${CYCLE} ==="
	  echo "  - Data path: ${RRFS_PATH}"
									
	  # remove previous log if exists
	  [ -f "${LOGFILE}" ] && rm -f "${LOGFILE}"

	  # submit the job to Slurm
	  sbatch -J "${JOBNAME}" \
             -o "${LOGFILE}" \
	         --export=YEAR=${YEAR},MONTH=${MM},DAY=${DD},HOUR=${HH},DATAPATH=${RRFS_PATH}/,DOMAIN="${DOMAIN_STR}" \
	         di_submit_jobs.sh					   			   			

    done
  done
done

