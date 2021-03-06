#---------------------------------------------------------------------------#
#Creates a multidem#
#---------------------------------------------------------------------------#

import pathlib
import numpy as np
import matplotlib.pyplot as plt
import scipy.io as sio
from mpl_toolkits.axes_grid1 import make_axes_locatable
import datetime as dt
import matplotlib.dates as mdates
from scipy.optimize import curve_fit 
from mpl_toolkits.basemap import Basemap
from matplotlib import animation
from matplotlib.gridspec import GridSpec


offset = 3500 #4350
max_frames = 4000
displayed_depth = 75
  
##########################################
# Load ADCD data
#########################################    

#Load TC-flach
#-------------------------    
#print(sio.whosmat(FILENAME))
if displayed_depth > 68:
    datafile_path = "/home/ole/windows/all_data/emb217/deployments/moorings/TC_Flach/ADCP1200/data/EMB217_TC-flach_adcp1200_val.mat"
else:    
    datafile_path = "/home/ole/windows/all_data/emb217/deployments/moorings/TC_Flach/ADCP600/data/EMB217_TC-flach_adcp600_val.mat"
data = sio.loadmat(datafile_path)
data = data["adcpavg"]
substructure = data.dtype

depth_flach = (data["depth"][0][0]).flatten()
number_of_depth_bins_flach = depth_flach.size
assert(np.mean(depth_flach)>0)

rtc = data["rtc"][0][0].flatten()
curr = data["curr"][0][0]

trim_emb217_flach = [0,8086]
rtc = rtc[0:8086]
curr = curr[0:8086,:]
 
print(np.shape(curr))   
all_west_east_flach = np.real(curr).T
all_north_south_flach = np.imag(curr).T

index_adcp_flach = np.argmin(np.abs(depth_flach-displayed_depth))
print("index_adcp_flach",index_adcp_flach)
#interpolate to fill in missing data (possible due to a constant timestep)
#index_adcp_flach = 29
temp_x = all_west_east_flach[index_adcp_flach,:]
temp_y = all_north_south_flach[index_adcp_flach,:]
xi = np.arange(len(temp_x))
mask = np.isfinite(temp_x)
west_east_flach = np.interp(xi, xi[mask], temp_x[mask])
north_south_flach = np.interp(xi, xi[mask], temp_y[mask])

#convert matlab time to utc
utc_flach = np.asarray(mdates.num2date(rtc-366))
print("utc flach:",np.shape(utc_flach),np.shape(west_east_flach))



#Load TC-tief
#-------------------------    
#print(sio.whosmat(FILENAME))
datafile_path = "/home/ole/windows/all_data/emb217/deployments/moorings/TC_Tief/adcp/data/EMB217_TC-tief_adcp300_val.mat"
data = sio.loadmat(datafile_path)
data = data["adcpavg"]
substructure = data.dtype

depth_tief = (data["depth"][0][0]).flatten()
number_of_depth_bins_tief = depth_tief.size
assert(np.mean(depth_tief)>0)

rtc = data["rtc"][0][0].flatten()
curr = data["curr"][0][0]

trim_emb217_tief = [100,8165]
rtc = rtc[100:8165]
    
all_west_east_tief = np.real(curr).T
all_north_south_tief = np.imag(curr).T

all_north_south_tief = all_north_south_tief[:,100:8165]
all_west_east_tief = all_west_east_tief[:,100:8165] 


index_adcp_tief = np.argmin(np.abs(depth_tief-displayed_depth))
print("index_adcp_tief",index_adcp_tief)

#interpolate to fill in missing data (possible due to a constant timestep)
#index_adcp_tief = 7
#print(np.shape(all_west_east_tief))
temp_x = all_west_east_tief[index_adcp_tief,:]
temp_y = all_north_south_tief[index_adcp_tief,:]
xi = np.arange(len(temp_x))
mask = np.isfinite(temp_x)
west_east_tief = np.interp(xi, xi[mask], temp_x[mask])
north_south_tief = np.interp(xi, xi[mask], temp_y[mask])

#print(np.shape(west_east_flach))
#print(np.shape(west_east_tief))

#convert matlab time to utc
utc_tief = np.asarray(mdates.num2date(rtc-366))




equal_time_index = np.argmin(np.abs(utc_flach-utc_tief[0]))
assert(equal_time_index!=0)
utc_flach = utc_flach[equal_time_index:]
west_east_flach = west_east_flach[equal_time_index:]
north_south_flach = north_south_flach[equal_time_index:]

#print(np.shape(utc_flach),np.shape(utc_tief))

if (utc_tief.size-utc_flach.size) > 0:
    west_east_flach = np.pad(west_east_flach,(0,utc_tief.size - utc_flach.size),'constant', constant_values=0)
    north_south_flach = np.pad(north_south_flach,(0,utc_tief.size - utc_flach.size),'constant', constant_values=0)



print(np.shape(west_east_flach),np.shape(west_east_tief))
print(utc_flach[0],utc_flach[-1])
print(utc_tief[0],utc_tief[-1])





#Load bathymetrie data
#-------------------------   
from PIL import Image
im = Image.open('/home/ole/windows/Area_of_interest.tif')
#im.show()
bathymetrie_array = np.array(im)
ny, nx = bathymetrie_array.shape


NCOLS = 320
NROWS = 103
XLLCORNER = 20.41776252494949
YLLCORNER = 57.30439748660123
CELLSIZE = 0.0010416666699999966
NODATA_VALUE = -32767.0
XRCORNER = XLLCORNER+nx*CELLSIZE
YRCORNER = YLLCORNER+ny*CELLSIZE

lons = np.arange(XLLCORNER,XRCORNER,CELLSIZE) 
lats  = np.arange(YLLCORNER,YRCORNER,CELLSIZE)  

lons = np.linspace(XLLCORNER,XLLCORNER+nx*CELLSIZE,nx) 
lats  = np.linspace(YLLCORNER,YLLCORNER+ny*CELLSIZE,ny)

emb217_flach = [57.3200,20.6150]
#print("emb217_flach",emb217_flach)

emb217_tief = [57.3200,20.600]
#print("emb217_tief",emb217_tief)


output_picture = plt.figure()#constrained_layout=True)
gs = GridSpec(2, 2, figure=output_picture, height_ratios = [4,1])
curr_axis = output_picture.add_subplot(gs[0, :])
tief_axis = output_picture.add_subplot(gs[1, 0])
flach_axis = output_picture.add_subplot(gs[1, 1])


#Set up the picture:
#output_picture, (curr_axis, flach_axis, tief_axis) = plt.subplots(nrows = 3, ncols = 1, gridspec_kw={'height_ratios': [3,1,1]})

map_ax = Basemap(ax=curr_axis, llcrnrlon= XLLCORNER, llcrnrlat= YLLCORNER, urcrnrlon = XRCORNER, urcrnrlat = YRCORNER, suppress_ticks=False)
#map_ax.drawcoastlines()


lons, lats = np.meshgrid(lons,lats)

xx, yy = map_ax(lons,lats)



#print(np.max(bathymetrie_array),np.min(bathymetrie_array))
levels = np.arange(50,110,5)
cntrf = map_ax.contourf(xx, yy,bathymetrie_array, levels,cmap="Blues", latlon = True)
cntr = map_ax.contour(xx, yy,bathymetrie_array, levels, colors ="black", latlon = True)

cbar = map_ax.colorbar(cntrf,location='right',pad='5%')
cbar.ax.invert_yaxis() 
cbar.set_label("depth [m]")

map_ax.plot(emb217_flach[1],emb217_flach[0],".",color = "red", latlon=True)
map_ax.plot(emb217_tief[1],emb217_tief[0],".", color = "green", latlon=True)


curr_axis.set_xlim(20.58,20.65)
curr_axis.set_ylim(YLLCORNER,57.34)

curr_axis.set_xlabel("longitude")
curr_axis.set_ylabel("latitude")

tief_axis.plot(utc_tief,west_east_tief[:],color = "tab:green", label = "WE")
tief_axis.plot(utc_tief,north_south_tief[:],color = "tab:blue", label = "NS")
flach_axis.plot(utc_tief,west_east_flach[:utc_flach.size],color = "tab:red", label = "WE")
flach_axis.plot(utc_tief,north_south_flach[:utc_flach.size],color = "tab:orange", label = "NS")

flach_axis.set_xlim(tief_axis.get_xlim())

flach_axis.xaxis.set_major_locator(mdates.DayLocator())
flach_axis.xaxis.set_minor_locator(mdates.HourLocator(byhour = [0,6,12,18],interval = 1))
hfmt = mdates.DateFormatter('%d %b')
flach_axis.xaxis.set_major_formatter(hfmt)
flach_axis.set_title("shallow mooring", fontweight="bold")
flach_axis.set_ylabel("velocity [m/s]")
flach_axis.set_ylim(-0.2,+0.2)
flach_axis.set_xlabel("2019")

tief_axis.set_xlabel("2019")
tief_axis.set_title("deep mooring", fontweight="bold")
tief_axis.set_ylabel("velocity [m/s]")

tief_axis.xaxis.set_major_locator(mdates.DayLocator())
tief_axis.xaxis.set_minor_locator(mdates.HourLocator(byhour = [0,6,12,18],interval = 1))
hfmt = mdates.DateFormatter('%d %b')
tief_axis.xaxis.set_major_formatter(hfmt)
#oxygen_axis.set_ylim(0,78)
tief_axis.set_ylim(-0.2,+0.2)



leg_flach = flach_axis.legend(loc = "upper right")
leg_tief = tief_axis.legend(loc = "upper left")

for line_flach,line_tief in zip(leg_flach.get_lines(),leg_tief.get_lines()):
    line_flach.set_linewidth(2.0)
    line_tief.set_linewidth(2.0)
    
#output_picture.subplots_adjust(top=0.939,bottom=0.081,left=0.08,right=0.939,hspace=0.196,wspace=0.12)
output_picture.subplots_adjust(top=0.944,bottom=0.066,left=0.06,right=0.979,hspace=0.166,wspace=0.12)

#axarr3[0].set_title(title_fig1,fontsize=16)
#axarr3[1].set_title(title_fig2,fontsize=16) 

output_picture.suptitle("ADCP measurements from emb217 in "+str(displayed_depth)+" m depth",fontsize=20,fontweight="bold")

output_picture.set_size_inches(18,10.5) #1.618*7.2,7.2)#


scale = 0.9

quiver_flach = curr_axis.quiver([emb217_flach[1]],[emb217_flach[0]],[west_east_flach[0]],[north_south_flach[0]], color = "red", alpha = 1, scale = scale)
quiver_tief = curr_axis.quiver([emb217_tief[1]],[emb217_tief[0]],[west_east_tief[0]],[north_south_tief[0]], color = "green", alpha = 1, scale = scale)

current_time_tief, = flach_axis.plot([mdates.date2num(utc_tief[offset]),mdates.date2num(utc_tief[offset])],[-1,1],"k-",lw=2)    
current_time_flach, = tief_axis.plot([mdates.date2num(utc_tief[offset]),mdates.date2num(utc_tief[offset])],[-1,1],"k-",lw=2)  

# initialization function: plot the background of each frame
def init():
    current_time_tief.set_data([],[])
    current_time_flach.set_data([],[])
    return tief_axis,flach_axis

step = 1
# animation function.  This is called sequentially
def animate(i,quiver_flach,quiver_tief):

    quiver_flach.set_UVC(west_east_flach[offset+i*step],north_south_flach[offset+i*step])
    quiver_tief.set_UVC(west_east_tief[offset+i*step],north_south_tief[offset+i*step])
    current_time_tief.set_data([mdates.date2num(utc_tief[offset+i*step]),mdates.date2num(utc_tief[offset+i*step])],[-1,1])
    current_time_flach.set_data([mdates.date2num(utc_tief[offset+i*step]),mdates.date2num(utc_tief[offset+i*step])],[-1,1])
    
    return flach_axis,tief_axis,quiver_flach,quiver_tief,


assert((max_frames+offset) < west_east_flach.size)
# call the animator.  blit=True means only re-draw the parts that have changed.
anim = animation.FuncAnimation(output_picture, animate, fargs = (quiver_flach,quiver_tief), init_func=init,
                               frames=max_frames, interval=10, blit=False)

# save the animation as an mp4.  This requires ffmpeg or mencoder to be
# installed.  The extra_args ensure that the x264 codec is used, so that
# the video can be embedded in html5.  You may need to adjust this for
# your system: for more information, see
# http://matplotlib.sourceforge.net/api/animation_api.html
anim.save("currents_animation_"+str(displayed_depth)+"m.mp4", fps=45, extra_args=['-vcodec', 'libx264'])
#anim.save('basic_animation.mp4', fps=30, extra_args=['-vcodec', 'libx264'])

#plt.show()


