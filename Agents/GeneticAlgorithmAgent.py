from Agent import *
import time
import math

class GeneticAlgorithmAgent(Agent):
    #implements the genetic algorithm proposed by Berghman, Goossens, and Leus

    def __init__(self, gameManager, verbose=False, seeCode=False, firstGuess = makeCode([1]*PIN_NUMBER), popSize = 150, maxGen = 100, maxSize = 60,
                 onePointCrossoverProb = .5, colorChangeProb = .03, permutationProb = .03, inversionProb = .02, a = 1, b = 2, EHatChoiceMethod = "min",
                 fitnessMethod = "changed", whatDoIfNoCodesFound = "random"):
        Agent.__init__(self, gameManager, verbose, seeCode)
        self.firstGuess = firstGuess # the paper recommends (1,1,2,3) -- "red red orange yellow" -- as an ideal first guess
        self.popSize = popSize + (popSize % 2)# the size of the initial population
        self.maxGen = maxGen # how many generations we go through
        self.maxSize = maxSize # how many eligible codes we consider after each use of the genetic algorithm

        self.onePointCrossoverProb = onePointCrossoverProb # probability that a given crossover is 1-point (as opposed to 2-point)
        self.colorChangeProb = colorChangeProb
        self.permutationProb = permutationProb
        self.inversionProb = inversionProb

        self.a = a # weight of black pins vs. white pins in the fitness function
        self.b = b # weight of the "slicking factor" in the fitness function

        self.EHatChoiceMethod = EHatChoiceMethod  # how an eligible population member is chosen as a guess
        # can equal "random" or "min"

        self.fitnessMethod = fitnessMethod  # if we change the fitness function or not
        # can equal "changed" or "original"

        self.whatDoIfNoCodesFound = whatDoIfNoCodesFound # what to do when the genetic algorithm doesn't find anything
        # can equal "random" or "continue"

        self.guessNumber = 0

    def canContinue(self, currentGen, EHatLength):
        if self.whatDoIfNoCodesFound == "random":
            return currentGen <= self.maxGen and EHatLength <= self.maxSize
        else:
            if currentGen > self.maxGen:
                if 0 < EHatLength <= self.maxSize:
                    if currentGen > self.maxGen+1:
                        print("Lesser wuh-oh. (" + str(currentGen) + ")")
                    return False
                else:
                    return True
            else:
                return EHatLength <= self.maxSize

    def createGuess(self):
        self.guessNumber += 1
        if self.guessNumber == 1:
            return self.firstGuess
        currentGen = 1
        EHat = []  # the set of eligible combinations created
        population = self.initializePopulation()
        # totMakeNew = 0
        # self.crossTime = 0
        # self.mutTime = 0
        # self.fitnessTime = 0
        # self.ATime = 0
        # self.BTime = 0
        # self.crossCalls = 0
        # self.mutCalls = 0
        # self.fitCalls = 0
        while (self.canContinue(currentGen, len(EHat))):
            # start = time.time()
            population = self.makeNewPopulation(population)   # deleted copy slicing operator here
            # totMakeNew += time.time() - start
            for code in population:
                if (self.isConsistent(code) and code not in EHat):   # check this
                    EHat.append(code)
                    if len(EHat) >= self.maxSize:
                        break
            currentGen += 1
        #print(len(EHat))
        # print("Make New Time:  ", totMakeNew)
        # print("  Crossover Time", self.crossTime, "/", self.crossCalls)
        # print("    Fitness Time", self.fitnessTime, "/", self.fitCalls)
        # print("     ATime       ", self.ATime)
        # print("     BTime       ", self.BTime)
        # print("  Mutation Time ", self.crossTime, "/", self.mutCalls)
        # print("  Mute Time     ", self.muteTime)
        # print("Is Consist Time:", totIsConsist)
        return self.chooseFromEHat(EHat)



    def initializePopulation(self):
        output = []
        for i in range(self.popSize):
            newCode = Code([])
            while newCode in output:
                newCode.randomize()
            output.append(newCode)
        return output

    def makeNewPopulation(self, pop):
        # start = time.time()
        output1 = self.crossover(pop)
        # self.crossTime += time.time() - start

        # start = time.time()
        output2 = self.mutate(output1)
        # self.mutTime += time.time() - start

        return output2

    def crossover(self, pop):
        #start = time.time()
        output = []
        # start = time.time()
        fitnesses = [self.fitness(popCode) for popCode in pop]
        # self.fitnessTime += time.time() - start

        randomParents = random.choices(pop, weights=fitnesses, k=self.popSize)

        for i in range(0, self.popSize, 2): # int(self.popSize / 2)):    # changed this loop, should work better
            parent1, parent2 = randomParents[i], randomParents[i+1]
            firstPins = parent1.getPinList()
            secondPins = parent2.getPinList()
            if random.random() < self.onePointCrossoverProb: # 1-point crossover
                crossoverPoint = random.randint(1, PIN_NUMBER-1)
                child1Colors = firstPins[:crossoverPoint] + secondPins[crossoverPoint:]
                child2Colors = secondPins[:crossoverPoint] + firstPins[crossoverPoint:]
            else: # 2-point crossover
                nums = list(range(1, PIN_NUMBER))
                crossoverPoint1 = random.choice(nums)
                nums.remove(crossoverPoint1)
                crossoverPoint2 = random.choice(nums)
                crossoverPoint1, crossoverPoint2 = min(crossoverPoint1, crossoverPoint2), max(crossoverPoint1, crossoverPoint2)
                child1Colors = firstPins[:crossoverPoint1] + secondPins[crossoverPoint1:crossoverPoint2] + firstPins[crossoverPoint2:]
                child2Colors = secondPins[:crossoverPoint1] + firstPins[crossoverPoint1:crossoverPoint2] + secondPins[crossoverPoint2:]
            child1 = Code(child1Colors)
            child2 = Code(child2Colors)
            output.append(child1)
            output.append(child2)
        # print("Rest time:", time.time()-fitdone)
        # self.crossCalls += 1
        return output

    def mutate(self, pop):
        output = []
        for code in pop:
            newPins = code.getPinList().copy()
            if random.random() <= self.colorChangeProb: # randomly change the color of a random pin
                pinToChange = random.randrange(PIN_NUMBER)
                oldColor = newPins[pinToChange].color
                newColor = random.choice([color for color in COLOR_LIST if color != oldColor])
                newPins = newPins[:pinToChange] + [CodePin(newColor)] + newPins[pinToChange+1:]
            if random.random() <= self.permutationProb: # switch the colors of two random positions
                nums = list(range(PIN_NUMBER))
                pin1 = random.choice(nums)
                nums.remove(pin1)
                pin2 = random.choice(nums)
                newPins[pin1], newPins[pin2] = newPins[pin2], newPins[pin1]
            if random.random() <= self.inversionProb: # invert the sequence of colors between two random positions
                nums = list(range(PIN_NUMBER))
                pin1 = random.choice(nums)
                nums.remove(pin1)
                pin2 = random.choice(nums)
                pin1, pin2 = min(pin1, pin2), max(pin1, pin2)
                newPins = newPins[:pin1] + newPins[pin2:pin1:-1] + [newPins[pin1]] + newPins[pin2+1:]
            newCode = Code(newPins)
            while newCode in output:
                newCode.randomize()
            output.append(newCode)
            # self.mutCalls += 1
        return output


    def fitness(self, code):
        output = 0
        output+=self.b*PIN_NUMBER*(self.guessNumber-2)
        pastGuesses = self.environment.getGuessList()
        pastClues = self.environment.getClueList()
        for i in range(self.guessNumber-1):
            prevGuess = pastGuesses[i]
            # start = time.time()
            newClue = code.getClue(prevGuess)   # This avoids calling getClue twice: this is the most expensive step
            # self.ATime += time.time() - start
            prevClue = pastClues[i]
            start = time.time()
            output += self.a*abs(newClue.getBlackPegs() - prevClue.getBlackPegs())
            output += abs(newClue.getWhitePegs() - prevClue.getWhitePegs())
            # self.BTime += time.time() - start
        # self.fitCalls+=1
        if self.fitnessMethod == "changed":
            return 1/(output+1)
        else:
            return output


    def chooseFromEHat(self, possibleCodes):
        # start = time.time()
        if len(possibleCodes) != 0:
            if self.EHatChoiceMethod == "min":
                output = possibleCodes[0]
                smallestRemaining = math.inf
                for c in possibleCodes:
                    cScore = 0
                    for cHat in possibleCodes:
                        if cHat != c:
                            hypoGuesses = self.environment.getGuessList() + [c]
                            hypoClues = self.environment.getClueList() + [cHat.getClue(c)]
                            for d in possibleCodes:
                                if d not in [c, cHat]:
                                    if isConsistent(d, hypoGuesses, hypoClues):
                                        cScore+=1
                    if cScore <= smallestRemaining:
                        output = c
                        smallestRemaining = cScore
            else:
                return random.choice(possibleCodes)
        else:
            print("Wuh-oh!")
            output = Code([])
            while (output in self.environment.getGuessList()) or (not self.isConsistent(output)):
                output.randomize()
        # print("Choice Time     ", time.time()-start)
        return output