import NarsGPT as NAR
#you can also exchange the NAR shell process with an I/O-compatible one:
#NAR.terminateNAR()
#NAR.setNAR(your spawned process I/O-compatible with ./NAR shell")

NAR.AddInput("*reset")
NAR.AddInput("<{garfield} --> cat>. :|:")
NAR.AddInput("cats are animals")
print(NAR.AddInput("<{?1} --> animal>?"))
print(NAR.AddInput("who is an animal?"))
