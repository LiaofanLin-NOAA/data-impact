from netCDF4 import Dataset

# -- change this --
#diag_file = "/scratch4/BMC/wrfruc/llin/2025-zrtrr2/240601_misc/20241213-ncdiag-rrfs-full/rrfs/na/prod/rrfs.20240927/06/diag_conv_t_anl.2024092706.nc4"   
#diag_file = "/scratch4/BMC/wrfruc/llin/2025-zrtrr2/240601_misc/20241213-ncdiag-rrfs-full/rrfs/na/prod/rrfs.20240927/06/diag_conv_fed_anl.2024092706.nc4"   
diag_file = "/scratch4/BMC/wrfruc/llin/2025-zrtrr2/240601_misc/20241213-ncdiag-rrfs-full/rrfs/na/prod/rrfs.20240927/06/diag_abi_g16_anl.2024092706.nc4"

with Dataset(diag_file, 'r') as nc:
    print("Variables in file:")
    for v in nc.variables:
        print(v)

    print("\nGlobal attributes:")
    for attr in nc.ncattrs():
        print(attr, "=", getattr(nc, attr))
