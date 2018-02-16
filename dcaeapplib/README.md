# dcaeapplib

Library for building DCAE analytics applications

# Example use:

```

class myapp:
  def __init__(self):
    # get the environment, and register callbacks for health checks and
    # configuration changes
    self.dcaeenv = dcaeapplib.DcaeEnv(healthCB=self.isHealthy, reconfigCB=self.reconfigure)
    # simulate a configuration change - we want the initial configuration
    self.reconfigure()
    # start the environment (to wait for health checks and config changes)
    self.dcaeenv.start()
    # begin processing loop
    while True:
      if self.configchanged:
	# fetch the updated configuration
        self.conig = self.dcaeenv.getconfig()
	self.configchanged = False
	# do any setup relevant to the configuration
      data = self.dcaeenv.getdata('myinputstream')
      # Data is a UTF-8 string, 'myinputstream' is this application's logical
      # name for this (one of potentially several) data sources.
      # Can also specify timeout_ms and limit as arguments.
      # timeout_ms (default 15,000) is the maximum time getdata() will block
      # limit is the maximum number of records retrieved at a time.
      # If no data is retrieved (timeout) the return will be None.
      if data is not None:
        # do something to process the data
	self.dcaeenv.senddata('myoutputstream', 'somepartitionkey', data)
	# data is a string, 'myoutputstream' is the application's logical
	# name for this (one of potentially several) data sinks.
	# somepartitionkey is used, by Kafka, to assign the data to a partition.

  def isHealthy(self):
    # return the health of the application (True/False)
    return True

  def reconfigure(self):
    # Do whatever needs to be done to handle a configuration change
    self.configchanged = True
```

# Environment Variables

This library uses the onap-dcae-cbs-docker-client library to fetch
configuration.  That library relies on the HOSTNAME and CONSUL_HOST
environment variables to find the configuration.

This library provides an HTTP interface for health checks.  By default this
listens on port 80 but can be overridden to use another port by setting the
DCAEPORT environment variable.  The HTTP interface supports getting 2 URLs:
/healthcheck, which will return a status of 202 (Accepted) for healthy,
and 503 (Service Unavailable) for unhealthy, and /reconfigure, which triggers
the library to check for updated configuration.

# Console Commands

This library provides a single console command "reconfigure.sh" which
performs an HTTP get of the /reconfigure URL
