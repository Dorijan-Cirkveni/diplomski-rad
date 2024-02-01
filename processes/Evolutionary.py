import random

from agents import Agent
import interfaces as itf


class Gene:
    def __init__(self, value: str, elmin, elmax):
        self.elmin = elmin
        self.elmax = elmax
        self.value = value

    def __copy__(self) -> 'Gene':
        return Gene(self.value, self.elmin, self.elmax)

    def use(self):
        return self.value

    def combine(self, other, cur=0, crossoverRate=0.1, randomSeed=None) -> tuple['Gene', int]:
        randomizer = random.Random(randomSeed) if randomSeed is not None else random.Random
        s1 = self.value
        s2 = other.value
        s = ''
        if randomizer.random() < crossoverRate:
            cur = 1 - cur
        for i in range(len(s1)):
            s += (s1, s2)[cur][i]
            if randomizer.random() < crossoverRate:
                cur = 1 - cur
        new = self.__copy__()
        new.value = s
        return new, cur

    def mutate(self, mutationRate=0.1, randomSeed=None) -> 'Gene':
        randomizer = random.Random(randomSeed) if randomSeed is not None else random.Random()
        s = ""
        for e in self.value:
            if randomizer.random() < mutationRate:
                e2 = chr(randomizer.randint(self.elmin, self.elmax))
                e = e2
            s += e
        new = self.__copy__()
        new.value = s
        return new


class iLifeform:
    def setRandomStats(self, randomSeed=None):
        raise NotImplementedError

    def combine(self, other, rate=0.1, randomSeed=None) -> 'iLifeform':
        raise NotImplementedError

    def mutate(self, rate=0.1, randomSeed=None) -> 'iLifeform':
        raise NotImplementedError

    def __copy__(self) -> 'iLifeform':
        raise NotImplementedError

    def makeNew(self, other, cRate, mRate, randomSeed) -> 'iLifeform':
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
        RES.append(fin_result)
    return RES, fin_result


class Selector(itf.iTrainingMethod):
    def __init__(self, lifeformTemplate,
                 populationSize=100, elitism=0.5, birthrate=2, cRate=0.1, mRate=0.1, combinationMethod=lambda L: sum(L),
                 randomSeed=None):
        super().__init__()
        self.randomizer: random.Random = random.Random(randomSeed) if randomSeed is not None else random.Random()
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
            RES.append(fin_result)
        return RES, fin_result

    def initiate(self, trainingSet: list[callable], randomSeed=None):
        self.population = []
        units = [self.template.__copy__() for _ in range(self.populationSize)]
        for unit in units:
            unit.setRandomStats(randomSeed)
        results, total = testAll(units, trainingSet)
        eval_results, eval_total = self.testAll(units, trainingSet)
        if len(results) != len(units):
            raise Exception(len(results), len(units))
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
            first = self.population[parent1]
            unit: iLifeform = first[0].makeNew(self.population[parent2][0],
                                               cRate=self.cRate,
                                               mRate=self.mRate,
                                               randomSeed=self.randomizer.randint(0, (1 << 32 - 1)))
            units.append(unit)
        results, new_total = testAll(units, trainingSet)
        eval_results, new_eval_total = testAll(units, evalSet)
        NET = (new_total, new_eval_total)
        newadditions = []
        while units:
            newadditions.append((units.pop(), results.pop(), eval_results.pop()))
        newadditions.sort(key=lambda E: E[1], reverse=True)
        newgeneration = self.population[:self.elitism] + newadditions
        self.population = newgeneration[:self.populationSize]
        self.population.sort(key=lambda E:E[1])
        new_total = self.combinationMethod([E[1] for E in self.population])
        new_eval_total = self.combinationMethod([E[2] for E in self.population])
        return NET, (new_total, new_eval_total)

    def runTestEval(self, trainingSet, evalSet, patience=10, maxIterations=1000):
        eval_log = [self.initiate(trainingSet)]
        best = eval_log[1]
        improvDeadline = 10
        lastBest = self.population
        for i in range(maxIterations):
            NET, ET = self.runGeneration(trainingSet, evalSet)
            if ET[1] < best:
                best = ET[1]
                lastBest = self.population
                improvDeadline = i + patience
            elif improvDeadline <= i:
                break


class ExampleLifeform(iLifeform):
    def __init__(self, s):
        self.gene = Gene(s, 49, 52)

    def setRandomStats(self, randomSeed=None):
        self.gene.mutate(1, randomSeed=randomSeed)

    def combine(self, other, rate=0.1, randomSeed=None):
        newGene, _ = self.gene.combine(other.gene, 0, rate, randomSeed=randomSeed)
        return ExampleLifeform(newGene)

    def mutate(self, rate=0.1, randomSeed=None):
        return ExampleLifeform(self.gene.mutate(rate).value)

    def __copy__(self):
        return ExampleLifeform(s=self.gene.__copy__())

    def generateAgent(self):
        return Agent.RecordedActionsAgent(self.gene.value)


def main():
    exmp = ExampleLifeform("121214312124")
    rand = random.Random(0)
    exmp2 = exmp.mutate(1)
    sel = Selector(exmp)
    return


if __name__ == "__main__":
    main()
