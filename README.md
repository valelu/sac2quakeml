# sac2quakeml
Converts event-info from SAC headers to QuakeML file using obspy (obspy.org).



Inputs from stdin:
- name of directory with SAC files
- strike,dip,rake of 2 nodal planes of events focal mechanism
- quakeml filename (if empty, output file is quake.ml)

Works only for 1 event in SAC files, otherwise the catalog is written without P/S picks and focal mechanisms.
Event origin is taken from sac.evla,sac.evlo and evdp. Origin time from sac.o given the reftime 
P and S picks are expected in sac.a and sac.t0 respectively. Other picks are omitted.
