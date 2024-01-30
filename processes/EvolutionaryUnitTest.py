import unittest

from Evolutionary import *


class TestSelector(unittest.TestCase):
    def setUp(self):
        # Initialize any required objects or configurations for testing
        pass

    def tearDown(self):
        # Clean up after each test
        pass

    def test_gene_combine(self):
        gene1 = Gene("111", 0, 1)
        gene2 = Gene("000", 0, 1)

        for seed in [42, 123, 999]:
            with self.subTest(seed=seed):
                new_gene, _ = gene1.combine(gene2, randomSeed=seed)

                self.assertTrue(isinstance(new_gene, Gene))
                self.assertNotEqual(new_gene.use(), "111")  # Adjusted this line

    def test_gene_mutate(self):
        gene = Gene("111", 0, 1)

        for seed in [42, 123, 999]:
            with self.subTest(seed=seed):
                new_gene = gene.mutate(mutationRate=0.5, randomSeed=seed)
                print(new_gene.use())
                self.assertTrue(isinstance(new_gene, Gene))
                self.assertNotEqual(new_gene.use(), "111")

    def test_selector_initiate(self):
        selector = Selector(lifeformTemplate=iLifeform(), populationSize=5)

        total, eval_total = selector.initiate(trainingSet=[lambda _: 1], randomSeed=42)

        self.assertEqual(total, eval_total)

    def test_selector_run_generation(self):
        selector = Selector(lifeformTemplate=iLifeform(), populationSize=5)

        _, eval_total_before = selector.initiate(trainingSet=[lambda _: 1], randomSeed=42)

        NET, ET = selector.runGeneration(trainingSet=[lambda _: 1], evalSet=[lambda _: 1])

        self.assertEqual(ET[1], eval_total_before)


def main():
    return


if __name__ == "__main__":
    main()
