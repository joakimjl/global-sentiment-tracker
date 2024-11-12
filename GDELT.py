# Basic use and new schema method
import gdelt

gd= gdelt.gdelt()

events = gd.Search(['2017 May 23'],table='events',output='gpd',normcols=True,coverage=False)

# new schema method
print(gd.schema('events'))
