import random
import interfaces as itf

class iGene:
    def __init__(self, value: str):
        self.value = value

    def use(self):
        raise NotImplementedError

    def combine(self, other, cur=0, crossoverRate=0.1, randomSeed=None):
        randomizer = random.Random(randomSeed) if randomSeed is not None else random.Random
        s1 = self.value
        s2 = other.value
        s = ''
        for i in range(len(s1)):
            s += (s1, s2)[cur][i]
            if randomizer.random() < crossoverRate:
                cur = 1 - cur
        return iGene(s), cur

    def mutate(self, mutationRate=0.1, randomSeed=None):
        randomizer = random.Random(randomSeed) if randomSeed is not None else random.Random
        s = ""
        for e in self.value:
            if randomizer.random() < mutationRate:
                e = chr(randomizer.randint(64, 127))
            s += e
        return iGene(s)


class iLifeform:
    def setRandomStats(self, randomSeed=None):
        raise NotImplementedError

    def combine(self, other, rate=0.1, randomSeed=None):
        raise NotImplementedError

    def mutate(self, rate=0.1, randomSeed=None):
        raise NotImplementedError

    def __copy__(self):
        raise NotImplementedError

    def makeNew(self,other,cRate,mRate,randomSeed):
        new:iLifeform=self.combine(other,cRate,randomSeed)
        return new.mutate(mRate)


class Selector(itf.iTrainingMethod):
    def __init__(self, lifeformTemplate, populationSize=100, elitism=0.5, birthrate=1, randomSeed=None):
        self.randomizer = random.Random(randomSeed) if randomSeed is not None else random.Random
        self.population: list = []
        self.populationSize = populationSize
        self.template = lifeformTemplate
        self.test: callable = testFunction
        self.elitism = int(populationSize * elitism) if elitism < 1 else elitism
        self.birthrate = birthrate

    def initiate(self, randomSeed=None):
        self.population = []
        for i in range(self.populationSize):
            unit: iLifeform = self.template.copy()
            unit.setRandomStats(randomSeed)
            score = self.test(unit)
            self.population.append((unit, score))

    def runGeneration(self):
        self.population:list
        X:list[iLifeform] = self.randomizer.sample(self.population, self.populationSize)
        for i in range(0,len(X)-1,2):
            unit: iLifeform = X[i].makeNew(X[i+1],randomSeed=self.randomizer.random())
            score = self.test(unit)
            self.population.append((unit, score))



def main():
    return


if __name__ == "__main__":
    main()
