#import NAR
import NarsGPT as NAR

NAR.AddInput("*reset")
NAR.AddInput("<{garfield} --> cat>. :|:")
NAR.AddInput("cats are animals")
print(NAR.AddInput("<{?1} --> animal>?"))
print(NAR.AddInput("who is an animal?"))
