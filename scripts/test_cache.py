from compas_cloud import Proxy
from compas.geometry import Point


p = Proxy()
p.restart()


def move_point(point):
    from compas.geometry import Translation

    return point.transformed(Translation.from_vector([1, 0, 0]))


# save the custom function to cloud
# cache=True means the function will return a cache object instead of the actual data
move_point_cloud = p.function(move_point, cache=True)

# Cache the input object to cloud
point = Point(0, 0, 0)
point_cache = p.cache(point)

# Call the function on cloud
# In this case, both input and output are cached objects, which is not sent back to client unless explicitly requested
result_cache = move_point_cloud(point_cache)
print(result_cache)
result = p.get(result_cache)
print(result)

# The cached output object can then be used as input directly on cloud
for i in range(3):
    result_cache = move_point_cloud(result_cache)
    print(result_cache)
    result = p.get(result_cache)
    print(result)
