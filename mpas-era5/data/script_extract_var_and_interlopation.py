import os
import sys
import datetime
import calendar

year = 2021

smonth = 1
emonth = 1
hour = 0

data_base = "/lustre/storm/nwp501/proj-shared/hgkang/data_for_others/MPAS_ML_data"
out_dir_base = ""

in_dir_base = os.path.join(data_base, "mpas_ORI_output")
out_dir_base = "/lustre/storm/nwp501/proj-shared/grnydawn/interpolated_mpas_output"
temp_dir_base = "/lustre/storm/nwp501/proj-shared/grnydawn/temp"

cmd = 'mkdir -p'+temp_dir_base
os.system(cmd)

ncks = '/sw/afw/spack-envs/base/opt/linux-sles15-x86_64/gcc-7.5.0/nco-5.0.1-7e43lbjezfph6ivvsbabfmuqy3mfdlin/bin/ncks'
ncremap = '/sw/afw/spack-envs/base/opt/linux-sles15-x86_64/gcc-7.5.0/nco-5.0.1-7e43lbjezfph6ivvsbabfmuqy3mfdlin/bin/ncremap'

for imm in range(smonth,emonth+1):
    days = calendar.monthrange(year, imm)[1]

    # job script initial
    cdate = datetime.date(year,imm,1)
    chour = datetime.time(0,0,0)
    ctime = datetime.datetime.combine(cdate,chour)

    cyyyy=ctime.strftime('%Y')
    cmm=ctime.strftime('%m')
    cdd=ctime.strftime('%d')
    chh=ctime.strftime('%H')

    inDir = in_dir_base + "/" + cyyyy + "/" + cmm

    outDir = out_dir_base + "/" + cyyyy + "/" + cmm
    cmd = 'mkdir -p '+outDir
    os.system(cmd)

    import pdb; pdb.set_trace()

    tempDir = temp_dir_base + "/" + cyyyy + "/" + cmm
    cmd = 'mkdir -p '+tempDir
    os.system(cmd)

    for idd in range(1,days+1):
        cdate = datetime.date(year,imm,idd)
        chour = datetime.time(hour,0,0)
        cdatehour = datetime.datetime.combine(cdate,chour)

        cyyyy=cdatehour.strftime('%Y')
        cmm  =cdatehour.strftime('%m')
        cdd  =cdatehour.strftime('%d')
        chh  =cdatehour.strftime('%H')

        ctime = cyyyy + cmm + cdd + chh

        print("-----------------------------------------------------------------------")
        print(ctime)

        mpasTimeFormat = cyyyy + '-' + cmm + '-' + cdd + '_' + chh+'.00.00'

        mpasOutputFileName = 'diag.'+mpasTimeFormat+'.nc'

        # Clean temp dir
        cmd1 = 'rm -f '+tempDir+'/*'
        os.system(cmd1)

        # Exclude vorticity field
        cmd1 = ncks + ' -C -O -x -v vorticity_50hPa,vorticity_100hPa,vorticity_200hPa,vorticity_250hPa,vorticity_500hPa,vorticity_700hPa,vorticity_850hPa,vorticity_925hPa,zgrid,zz,fzm,fzp ' + inDir + mpasOutputFileName + ' '+tempDir+'/temp1.nc'
        os.system(cmd1)

        # Remapping
        cmd1 = ncremap + ' -m map_MPASA_QU20km_to_1440x720_bilinear.nc '+tempDir+'/temp1.nc '+tempDir+'/temp2.nc'
        os.system(cmd1)

        outFileName = 'mpaso_out_1440x720_f48_'+mpasTimeFormat+'.nc'

        # Move files
        cmd1 = 'mv '+tempDir+'/temp2.nc '+ outDir + "/" + outFileName
        os.system(cmd1)
