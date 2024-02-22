import unittest

from Evolutionary import *


class SimpleLifeform(iLifeform):
    def __init__(self, gene_value="111"):
        self.gene = Gene(gene_value, 49, 52)

    def setRandomStats(self, randomSeed=None):
        pass

    def combine(self, other, rate=0.1, randomSeed=None) -> 'iLifeform':
        other:SimpleLifeform
        new_gene, _ = self.gene.combine(other.gene, randomSeed=randomSeed, crossoverRate=rate)
        new_lifeform = SimpleLifeform()
        new_lifeform.gene = new_gene
        return new_lifeform

    def mutate(self, rate=0.1, randomSeed=None) -> 'iLifeform':
        new_gene = self.gene.mutate(mutationRate=rate, randomSeed=randomSeed)
        new_lifeform = SimpleLifeform()
        new_lifeform.gene = new_gene
        return new_lifeform

    def __copy__(self) -> 'iLifeform':
        new_lifeform = SimpleLifeform()
        new_lifeform.gene = self.gene.__copy__()
        return new_lifeform

    def generateAgent(self):
        pass


class TestSelector(unittest.TestCase):
    def setUp(self):
        # Initialize any required objects or configurations for testing
        pass

    def tearDown(self):
        # Clean up after each test
        pass

    def test_gene_combine(self):
        lifeform1 = SimpleLifeform()
        lifeform2 = SimpleLifeform('000')

        for seed, value in {42: '101', 123: '010', 999: '100'}.items():
            with self.subTest(seed=seed):
                new_lifeform = lifeform1.combine(lifeform2, rate=0.5, randomSeed=seed)

                self.assertTrue(isinstance(new_lifeform, SimpleLifeform))
                self.assertEqual(new_lifeform.gene.use(), value)

    def test_gene_mutate(self):
        lifeform = SimpleLifeform()

        for seed, value in {42: '132', 123: '111', 999: '143'}.items():
            with self.subTest(seed=seed):
                new_lifeform = lifeform.mutate(rate=0.5, randomSeed=seed)
                self.assertTrue(isinstance(new_lifeform, SimpleLifeform))
                self.assertEqual(new_lifeform.gene.use(), value)

    def test_selector_initiate(self):
        selector = Selector(lifeformTemplate=SimpleLifeform(), populationSize=5)

        total, eval_total = selector.initiate(trainingSet=[lambda _: 1], randomSeed=42)

    def test_selector_run_generation(self):
        selector = Selector(lifeformTemplate=SimpleLifeform(), populationSize=5)

        _, eval_total_before = selector.initiate(trainingSet=[lambda _: 1], randomSeed=42)

        NET, ET = selector.runGeneration(trainingSet=[lambda _: 1], evalSet=[lambda _: 1])


def main():
    return


if __name__ == "__main__":
    main()
