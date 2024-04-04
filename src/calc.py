
# Import things that are needed generically
import math
import re
from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import BaseTool, StructuredTool, tool
from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)


def extract_numbers(string):
    # Regular expression to find int or float numbers
    pattern = r"[-+]?\d*\.\d+|\d+"
    numbers = re.findall(pattern, string)
    # Convert strings to int or float
    numbers = [int(num) if '.' not in num else float(num) for num in numbers]
    return numbers


class BeamData(BaseModel):
    data: str = Field(description="problem data")
    # b: float = Field(description="width", default=300)
    # h: float = Field(description="depth", default=500)
    # fc: float = Field(description="concrete compressive strength", default=27)
    # fy: float = Field(description="steel yield strength", default=414)
    # m: float = Field(description="bending moment", default=25)
    # v: float = Field(description="shear force", default=25)


class BeamCalcTool(BaseTool):
    name = "Beam Calculator"
    description = "useful for when you need to answer questions about the problem"
    args_schema: Type[BaseModel] = BeamData
    return_direct: bool = True

    def _run(
        self,
        beam_data: str,
        # b: float, d: float,
        # fc: float, fy: float,
        # m: float, v: float,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> float:
        """Use the tool."""
        _dat = extract_numbers(beam_data)
        passed_result = 1
        if len(_dat) == 6:
            [b, d, fc, fy, m, v] = _dat
        else:
            [b, d, fc, fy, m, v, passed_result] = _dat
        # Mu = 0.9 * b * d * d * fc * w * (1 - (0.59 * w))
        print(b, d, fc, fy, m, v, passed_result)
        k_factor = 0.718
        Ru = 0.9 * b * d * d * fc
        lim = 1.694 * m * 1000000 / Ru
        if not lim < k_factor:
            return 0
        w = math.sqrt(k_factor - lim) + k_factor
        rho = fc * w / fy
        rebar = rho * b * d
        valid = False
        if passed_result / int(rebar) < 1.02 and passed_result / int(rebar) > 0.98:
            return 'within 2 percent.'

        result = beam_data + ' | ' + str(int(rebar))
        return result

    async def _arun(
        self,
        beam_data: str,
        # b: float, d: float,
        # fc: float, fy: float,
        # m: float, v: float,
        run_manager: Optional[AsyncCallbackManagerForToolRun] = None,
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")
