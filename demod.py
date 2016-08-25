#!/bin/python3

#DEMODULATING THE RDS SIGNAL AND DUMPING RECEIVED PACKETS

#Tarmo Tanilsoo, 2016


import wave
import array
import time
from math import pi
from numpy import arctan2 as atan2, absolute, std, diff, copy, sort
from bitarray import bitarray

def codeVector(block):
    global matrix
    vector=bitarray("0000000000")
    for i in range(len(block)):
        if block[i]:
            vector=vector^matrix[i]
    return block+vector

def binaryToHEX(binary):
    return hex(int(binary.to01(),2))[2:].zfill(4).upper()

#Tables for error checking
matrix=[bitarray("0001110111"),
        bitarray("1011100111"),
        bitarray("1110101111"),
        bitarray("1100001011"),
        bitarray("1101011001"),
        bitarray("1101110000"),
        bitarray("0110111000"),
        bitarray("0011011100"),
        bitarray("0001101110"),
        bitarray("0000110111"),
        bitarray("1011000111"),
        bitarray("1110111111"),
        bitarray("1100000011"),
        bitarray("1101011101"),
        bitarray("1101110010"),
        bitarray("0110111001")]
offsetWords=[bitarray("0011111100"),
             bitarray("0110011000"),
             bitarray("0101101000"),
             bitarray("1101010000"),
             bitarray("0110110100")]

#CONFIG

sampleRate=47500 #Sample rate that is multiple of 1187.5 is being used for simplicity purposes.
iterationStep=int(sampleRate/1187.5)
verbose=False #Output additional information for debugging/experimentation purposes
rawOutput=False #If true, output only count of block A decodes and incorrect blocks rate.

phaseDifferenceLimitOffset=1.38
phaseDifferenceMinimum=pi-phaseDifferenceLimitOffset
phaseDifferenceMaximum=pi+phaseDifferenceLimitOffset

#LOADING THE FILE, DEMODULATING AND FETCHING THE BITSTREAM

if verbose: print("Loading the data file...")
audioRecordingFile=wave.open("waveform.wav")
audioContent=array.array("h",audioRecordingFile.readframes(-1))
audioRecordingFile.close()

contentSize=len(audioContent)
maxPacketsCount=int((len(audioContent)/sampleRate/2)*(1187.5/104))

#Audio components
audioQ=audioContent[::2]
audioI=audioContent[1::2]

#PROCESSING
#We are storing all our tries
allBits=[]
allCounts=[]
allBlocksA=[]
packets=[]
if not rawOutput: print("Processing...")
for i in range(iterationStep): #We'll find an optimal starting point for the decoding.
    phases=atan2(audioQ[i::iterationStep],audioI[i::iterationStep])
    bits=absolute(diff(phases)) #Technically phase differences at initialization time, but we'll transform it to bits, as we are dealing with DPSK with 2 states.
    bits[bits > phaseDifferenceMaximum]=0
    bits[bits < phaseDifferenceMinimum]=0
    bits=bitarray(bits.tolist()) #Convert to bitarray
    #Now we start looking for PI code.
    for j in range(len(bits)-104): #We'll search through entire bitstream. Might be useful during low signal conditions
        blockA=bits[j:j+26]
        payloadA=blockA[0:16]
        expectedBlockA=codeVector(payloadA) #Code vector
        expectedBlockA[16:26]^=offsetWords[0]
        if blockA == expectedBlockA: #PI found!
            foundBlocksA=bits.search(blockA)
            currentCount=len(foundBlocksA)
            piCode=binaryToHEX(payloadA)
            allBits.append(bits)
            allCounts.append(currentCount)
            allBlocksA.append(blockA) #Store received block A
            if verbose: print("PI (%s) found! Total occurrences: %i" % (piCode,currentCount))
            break

#We will now determine the bitstream we will work on going forward.
if verbose: print("Determining the best decoding result...")
allCountsMax=max(allCounts)
finalBlockA=None
finalBits=None
if allCounts.count(allCountsMax) >= 2: #Ideal situation when there are plentiful of good choices.
    bitstreamMatches=0
    for k in range(len(allCounts)): #Search for a bit stream that repeats the most in various iterations.
        if allCounts[k] == allCountsMax:
            currentBits=allBits[k]
            matchesCount=allBits.count(currentBits)
            if matchesCount > bitstreamMatches:
                finalBlockA=allBlocksA[k]
                finalBits=currentBits
                bitstreamMatches=matchesCount
else: #In case of low signal conditions where we only have 1 stream with maximum block A decodes...
    bestIndex=allCounts.index(allCountsMax)
    finalBits=allBits[bestIndex]
    finalBlockA=allBlocksA[bestIndex]
    
if verbose: print("Locating the first block A in the data...")

foundABlocks=finalBits.search(finalBlockA)
pointer=foundABlocks[0] #Let's go straight to the beginning of first full packet. By not searching bit-by-bit we save CPU time. This does mean recording must be continuous for the duration of the file!

if verbose: print("Error checking and packet dump...")

packetsOut=[]
lastSuccessfulBlock=0 #Index of a last successfully decoded block.

foundPIs=[] #We list all decoded PIs here. In general, there should only be one, but in low signal conditions we may have bad decodes that look legit. Hence we'll do a popularity contest at the end.
foundPICounts=[] #We list counts for each PIs here.
failCount=0 #Amount of failed packet decodes. Hence each failed block only increments it by 1/4.
while pointer <= len(finalBits)-104:
    dataRowSegments=["????"]*4 #Reset the packet data
    blockIndex=0
    if verbose: print("Pointer position: %i " % (pointer))
    #Trying to decode groups
    offsetWordIndexes=[0,1,2,4]
    while blockIndex < 4:
        block=finalBits[pointer:pointer+26]
        payload=block[0:16]
        expectedBlock=codeVector(payload)
        expectedBlock[16:26]^=offsetWords[offsetWordIndexes[blockIndex]]
        if block == expectedBlock: #Successful decode of a block
            if verbose: print("DECODE")
            blockContent=binaryToHEX(payload)
            dataRowSegments[blockIndex]=blockContent
            if blockIndex == 0: #If decoded group A
                if blockContent in foundPIs: #Register detected PI. At the end of the process, these PIs will be counted and the one with highest count will be regarded as actual PI.
                    foundPICounts[foundPIs.index(blockContent)]+=1
                else:
                    foundPIs.append(blockContent)
                    foundPICounts.append(0)
        else:
            if verbose: print("No decode")
            #Before writing this block completely off, see if we're in sync
            distancesToKnownBlockAs=list(filter(lambda x:x>0,map(lambda x:x-pointer,foundABlocks)))
            if(len(distancesToKnownBlockAs) > 0): #If we haven't gone past the last block A
                bitsToNextKnownBlockA=min(distancesToKnownBlockAs) #Bits to next known A-block in the bitstream
                bitDistanceModulus=bitsToNextKnownBlockA % 26
                if bitDistanceModulus != 0 and bitsToNextKnownBlockA < 104: #If that distance is not divisible by 26 indicating we may be off and we are close to known Block A. We don't know when the discontinuity was introduced.
                    positionCorrection=bitDistanceModulus if bitDistanceModulus <= 13 else bitDistanceModulus-26 #Resync to closest expected block beginning
                    pointer+=positionCorrection
                    estimatedCurrentBlockIndex=4-int((bitsToNextKnownBlockA-positionCorrection)/26)
                    blockIndex=estimatedCurrentBlockIndex+1 if positionCorrection<0 else estimatedCurrentBlockIndex
                    if verbose:
                        print("LOSS OF SYNC DETECTED!")
                        print("Next block A is %i bit(s) away. This is not divisible by 26." % (bitsToNextKnownBlockA))
                        print("Moving pointer by %i bit(s). Negative values mean rewinding." % positionCorrection)
                        print("Estimated blockIndex %i, new blockIndex %i" % (estimatedCurrentBlockIndex,blockIndex))
                    continue #Try to get this block again at the position we found.
            failCount+=0.25
        blockIndex+=1
        pointer+=26
    packetsOut.append(" ".join(dataRowSegments)+"\n")
if verbose: print("Saving...")

##DETERMINING MOST ENCOUNTERED PI CODE AND FINISHING UP

finalPICount=max(foundPICounts)
if finalPICount > 1:
    finalPI=foundPIs[foundPICounts.index(finalPICount)]
    if not rawOutput:
        print("===================== COMPLETE =========================")
        print("Detected PI code: \t%s" % (finalPI))
        print("Detected A-blocks: \t%i" % (allCountsMax))
        print("Incorrect blocks: \t%.1f %%" % (failCount/len(packetsOut)*100))
    else:
        print("%i %.3f" % (allCountsMax, (failCount/len(packetsOut)*100)))
else:
    finalPI="UNKNOWN"
    if not rawOutput:
        print("=================== DECODE FAILED ======================")
        print("No conclusive PI codes found")
    else:
        print("0 100")
#DUMP TO FILE
outFile=open(finalPI+".txt","w")
outFile.writelines(packetsOut)
outFile.close()
if not rawOutput:
    print("___________________________________")
    print("Packets have been saved to "+finalPI+".txt\n")
