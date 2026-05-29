from __future__ import annotations

import sys
import unittest
from pathlib import Path


ALG_DIR = Path(__file__).resolve().parents[1]
if str(ALG_DIR) not in sys.path:
    sys.path.insert(0, str(ALG_DIR))

from models import Problema
from simplex import simplex


class SimplexTestCase(unittest.TestCase):
    def test_resolve_problema_com_solucao_unica(self) -> None:
        problema = Problema(
            c=[40.0, 35.0],
            A=[[2.0, 3.0], [4.0, 3.0]],
            b=[60.0, 96.0],
        )

        x, z, status = simplex(problema)

        self.assertEqual(status, "otimo")
        self.assertAlmostEqual(x[0], 18.0)
        self.assertAlmostEqual(x[1], 8.0)
        self.assertAlmostEqual(z, 1000.0)

    def test_identifica_problema_ilimitado(self) -> None:
        problema = Problema(
            c=[40.0, 35.0],
            A=[[-1.0, 0.0], [0.0, -1.0]],
            b=[60.0, 96.0],
        )

        with self.assertRaisesRegex(ValueError, "ilimitado"):
            simplex(problema)

    def test_identifica_multiplas_solucoes(self) -> None:
        problema = Problema(
            c=[2.0, 4.0],
            A=[[1.0, 2.0], [1.0, 0.0]],
            b=[4.0, 2.0],
        )

        x, z, status = simplex(problema)

        self.assertEqual(status, "multiplas_solucoes")
        self.assertAlmostEqual(z, 8.0)
        self.assertLessEqual(x[0] + 2 * x[1], 4.0)


if __name__ == "__main__":
    unittest.main()
