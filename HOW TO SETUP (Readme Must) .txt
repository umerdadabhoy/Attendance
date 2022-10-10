-protect machine with super user
-reserve IP address on the router connected with machine
-Mac bind that IP address reserved earlier
	
	-Allow ping wifi devices on network from security option in router

-Port forward that IP address with the port selected in machine (default 4370)

step internet: IF that is ISP router bind ddns link with the port of server(not device) , 
		install utility (no-ip , UDC(make it run on startup)) to keep dynamic Ip always linked

-IF not then go to next router in LAN
-Assign previous router IP/mac binding , address reservation
-Map port forwarding with bounded IP of previous router

:perform above 33 steps until ISP router

-Assign server computer(prefer with ISP router) a reserved address and IP/mac binding  
:perform step internet 