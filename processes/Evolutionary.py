import random


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
    def setRandomStats(self):
        raise NotImplementedError

    def combine(self, other, rate=0.1, randomSeed=None):
        raise NotImplementedError

    def mutate(self, rate=0.1, randomSeed=None):
        raise NotImplementedError


class Selector:
    def __init__(self, lifeformTemplate, testFunction, population=100, elitism=0.5, birthrate=1):
        self.population = []
        self.template = lifeformTemplate
        self.test: callable = testFunction
        self.population = population
        self.elitism = int(population * elitism) if elitism < 1 else elitism
        self.birthrate = birthrate


def main():
    return


if __name__ == "__main__":
    main()
