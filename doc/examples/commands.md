= Example commands of usage =

AQStat is a handy tool to visualize data produced by the sensor network of sensor.community. In the followings you will see examples of the main usage.

== Help ==

Get a general help of `aqstat`:

```
python bin\aqstat --help
```

Get a general help of the `download` command:

```
python bin\aqstat download --help
```

== Download ==

Download all daily data from https://archive.sensor.community into folder `data`
for sensor ID `39718` between given dates in verbose mode:

```
python bin/aqstat -v download data 39718 --date-start 2020-05-28 --date-end 2020-08-31
```

== Plot ==

Plot all individual PM-related data from folder `data`
for sensor name `Verõce-Zentai`:

```
python bin/aqstat plot data -n Verõce-Zentai -p
```

Pl
