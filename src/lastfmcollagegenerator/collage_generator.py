from PIL import Image

from lastfmcollagegenerator.collage import CollageBuilderFactory, LastfmConfig, \
    CollageBuilderConfig, BaseCollageBuilder
from lastfmcollagegenerator.constants import ENTITIES, PERIODS
from lastfmcollagegenerator.lastfm.client import LastfmClient


class CollageGenerator:
    """
    Generates a NxN collage with the covers of a Last.fm
    user tops of a given period.
    """
    MAX_COLS = 5
    MAX_ROWS = 5

    def __init__(self, lastfm_api_key: str, lastfm_api_secret: str):
        self.lastfm_config = LastfmConfig(
            lastfm_api_key=lastfm_api_key,
            lastfm_api_secret=lastfm_api_secret
        )

    def generate(
            self,
            entity: str,
            username: str,
            cols: int,
            rows: int,
            period: str
    ) -> Image:
        self._validate_parameters(entity, cols, rows, period)
        collage_builder = self._get_collage_builder(entity, cols, rows, period)
        return collage_builder.create(username)

    def _get_collage_builder(
            self,
            entity: str,
            cols: int,
            rows: int,
            period: str
    ) -> BaseCollageBuilder:
        collage_builder_config = CollageBuilderConfig(
            cols=cols,
            rows=rows,
            period=period,
        )
        lastfm_client = LastfmClient(
            api_key=self.lastfm_config.lastfm_api_key,
            api_secret=self.lastfm_config.lastfm_api_secret
        )
        return CollageBuilderFactory(
            entity=entity,
            config=collage_builder_config,
            lastfm_client=lastfm_client
        )

    def _validate_parameters(
            self,
            entity: str,
            cols: int,
            rows: int,
            period: str
    ):
        if entity not in ENTITIES:
            raise ValueError(
                f"Invalid entity: {entity}. "
                f"Options are: {ENTITIES}"
            )
        if cols > self.MAX_COLS or rows > self.MAX_ROWS:
            raise ValueError(
                f"Invalid number of columns or rows: {cols}x{rows}: "
                f"Max values are: {self.MAX_ROWS}x{self.MAX_COLS}"
            )
        if period not in PERIODS:
            raise ValueError(
                f"Invalid period: {period}. "
                f"Options are: {PERIODS}"
            )
