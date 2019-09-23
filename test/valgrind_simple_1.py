# Here is super simple script that shouldn't cause a race condition.
# We will test it with valgrind, if valgrind finds a problem with it we will
# stop using valgrind as a tool for testing race conditions

print("hello world")
