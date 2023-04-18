import obspy
import os
from obspy.core import UTCDateTime
from obspy.io.sac import sactrace

sac_dir=input("PLEASE, enter name of directory containing your sac files:")

sac_files=[os.path.join(sac_dir,sf) for sf in os.listdir(sac_dir) if os.path.isfile(os.path.join(sac_dir,sf))]
catalog=obspy.core.event.Catalog()
#print(sac_files)
#st=obspy.read(pathname_or_url=sfiles)#,format='SAC') #read sac_file to obspy stream
#leave only sac trace files in the file lise:
for sf in sac_files:
   try:
     st=obspy.read(sf,format='SAC')
   except obspy.io.sac.util.SacIOError:
     print('File ',sf,'is not sac trace file, probably response file. Skipping.')
     sac_files.remove(sf)

#read sac headers
for sf in sac_files:
   sac_head=sactrace.SACTrace.read(sf,headonly=True) #sac header
   #extract event info
   if len(catalog)==0: #catalog is empty
    ev_name=sac_head.kevnm #sac event name as resource_id
    #generate Origin from
    #sac_head.o
    #sac_head.evla
    #sac_head.evlo
    #sac_head.evdp
    Origin=obspy.core.event.origin.Origin(time=UTCDateTime(sac_head.reftime+sac_head.o), longitude=sac_head.evlo, latitude=sac_head.evla, depth=sac_head.evdp)
    Magnitude=obspy.core.event.magnitude.Magnitude(mag=sac_head.mag) 
    event=obspy.core.event.Event(resource_id=obspy.core.event.ResourceIdentifier(id=ev_name), origins=[Origin],magnitudes=[Magnitude])
    catalog=obspy.core.event.Catalog(events=[event])
   #check if event exists...
   else:
    if not (UTCDateTime(sac_head.reftime+sac_head.o) in [e.origins[0].time for e in catalog] and 
       sac_head.evlo in [e.origins[0].longitude for e in catalog]   and 
       sac_head.evla in [e.origins[0].latitude for e in catalog] and 
       sac_head.evdp in [e.origins[0].depth for e in catalog] and 
       sac_head.mag in [e.magnitudes[0].mag for e in catalog]):
    #if not (orig==Origin and magn==Magnitude):     not working probably due to resource_id....
      orig=obspy.core.event.origin.Origin(time=UTCDateTime(sac_head.reftime+sac_head.o), longitude=sac_head.evlo, latitude=sac_head.evla, depth=sac_head.evdp)
      magn=obspy.core.event.magnitude.Magnitude(mag=sac_head.mag) 
      ev2=obspy.core.event.Event(resource_id=obspy.core.event.ResourceIdentifier(id=sac_head.kevnm), origins=[orig],magnitudes=[magn])
      catalog.append(ev2)

print('Found ',len(catalog),' events in sac files in directory: ',sac_dir)

#extract picks and add to first event in catalog #WARNING FOR CATALOGS LONGER THAN 1 THIS IS OMITTED
print('Obtaining picks:')
if len(catalog)==1:
   event=catalog[0]
   picks=[]
   for sf in sac_files:
       sac_head=sactrace.SACTrace.read(sf,headonly=True) #read sac header
       wfid=obspy.core.event.WaveformStreamID(network_code=sac_head.knetwk,station_code=sac_head.kstnm,channel_code=sac_head.kcmpnm) #prepare waveform_id for stream identification
       if not sac_head.a==None: #if not empty -> associate as P pick'
          print('Adding pick found in sac.header.a as P from ',wfid.get_seed_string())
          pick=obspy.core.event.origin.Pick(time= sac_head.reftime+sac_head.a, waveform_id=wfid,phase_hint='P')
          picks.append(pick)
       if not sac_head.t0==None: #if not empty -> associate as S pick'
       	  print('Adding pick found in sac.header.t0 as S from ',wfid.get_seed_string())
          pick=obspy.core.event.origin.Pick(time= sac_head.reftime+sac_head.t0, waveform_id=wfid,phase_hint='S')
          picks.append(pick)
   event.picks=picks #append picks to event
   print('Adding nodal planes to event:')
   print(event.origins[0])
   #input in str,dp,rk on 1 line 
   str1, dip1, rake1=input('PLEASE, enter strike,dip,rake of nodal plane 1:').split()
   str2, dip2, rake2=input('PLEASE, enter strike,dip,rake of nodal plane 2:').split()
   nodals1=obspy.core.event.source.NodalPlane(strike=str1,dip=dip1,rake=rake1) #generate NP object for first NP
   nodals2=obspy.core.event.source.NodalPlane(strike=str2,dip=dip2,rake=rake2) #generate NP object for second NP

   event.focal_mechanisms=[obspy.core.event.source.FocalMechanism(nodal_planes=obspy.core.event.source.NodalPlanes(nodal_plane_1=nodals1,nodal_plane_2=nodals2))] #associate NP info to focal mechanism of event
   catalog[0]=event #rewrite in catalog with added info
#print(event)
#Write quake ML file
print('Writing QUAKEML file')
outfile=input('please, enter name of quakeml file:')#'quake.ml'
if outfile=='': #if no file name from user use default:
  outfile='quake.ml'
catalog.write(filename=outfile,format='QUAKEML')

