import math
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

    def makeNew(self, other, cRate, mRate, randomSeed):
        new: iLifeform = self.combine(other, cRate, randomSeed)
        return new.mutate(mRate)

    def generateAgent(self):
        raise NotImplementedError


def testAll(population, testSet: list[callable], combinationMethod=lambda L: sum(L)):
    RES = []
    fin_result = 0
    for unit in population:
        unit: iLifeform
        results = [fn(unit) for fn in testSet]
        fin_result = combinationMethod(results)
    return RES, fin_result


class Selector(itf.iTrainingMethod):
    def __init__(self, lifeformTemplate, agentTemplate,
                 populationSize=100, elitism=0.5, birthrate=2, cRate=0.1, mRate=0.1, combinationMethod=lambda L: sum(L),
                 randomSeed=None):
        super().__init__(agentTemplate)
        self.randomizer = random.Random(randomSeed) if randomSeed is not None else random.Random
        self.population: list = []
        self.template = lifeformTemplate

        self.populationSize = populationSize
        self.elitism = int(populationSize * elitism) if elitism < 1 else elitism
        self.birthrate = birthrate
        self.cRate = cRate
        self.mRate = mRate
        self.combinationMethod = combinationMethod

    def testAll(self, population, testSet: list[callable]):
        RES = []
        fin_result = 0
        for unit in population:
            unit: iLifeform
            results = [fn(unit) for fn in testSet]
            fin_result = self.combinationMethod(results)
        return RES, fin_result

    def initiate(self, trainingSet: list[callable], randomSeed=None):
        self.population = []
        units = [self.template.copy() for _ in range(self.populationSize)]
        for unit in units:
            unit.setRandomStats(randomSeed)
        results, total = testAll(units, trainingSet)
        eval_results, eval_total = testAll(units, trainingSet)
        while units:
            self.population.append((units.pop(), results.pop(), eval_results.pop()))
        self.population.sort(key=lambda E: E[1], reverse=True)
        return total, eval_total

    def selectParents(self):
        L = []
        for i in range((self.populationSize - self.elitism) * self.birthrate):
            a = self.randomizer.randint(0, self.populationSize - 1)
            b = self.randomizer.randint(0, self.populationSize - 2)
            if b >= a:
                b += 1
            L.append((a, b))
        return L

    def runGeneration(self, trainingSet: list[callable], evalSet: list[callable]):
        self.population: list
        units = []
        for (parent1, parent2) in self.selectParents():
            unit: iLifeform = self.population[parent1].makeNew(self.population[parent2],
                                                               cRate=self.cRate,
                                                               mRate=self.mRate,
                                                               randomSeed=self.randomizer.random())
            units.append(unit)
        results, new_total = testAll(units, trainingSet)
        eval_results, new_eval_total = testAll(units, evalSet)
        newadditions = []
        while units:
            newadditions.append((units.pop(), results.pop(), eval_results.pop()))
        newadditions.sort(key=lambda E: E[1], reverse=True)
        newgeneration = self.population[:self.elitism] + newadditions
        self.population = newgeneration[:self.populationSize]
        self.population.sort()
        return

class ExampleLifeform(iLifeform):
    def self

    def setRandomStats(self, randomSeed=None):
        pass

    def combine(self, other, rate=0.1, randomSeed=None):
        pass

    def mutate(self, rate=0.1, randomSeed=None):
        pass

    def __copy__(self):
        pass

    def generateAgent(self):
        pass


def main():
    return


if __name__ == "__main__":
    main()
