from worker.analysis.ndvi import NDVIAnalyzer
from worker.utils.vigilante import Vigilante
from worker.models.analyze_request import AnalyzeRequest

from worker.utils.database import SyncPostgreSQLController
from worker.utils.extractor import Extractor
import os


def test():
    v = Vigilante("test_worker", True, True, os.getcwd() + "/worker_logs/")
    db = SyncPostgreSQLController()
    ndvi = NDVIAnalyzer(v.get_logger(), db, "huitest")
    ext = Extractor()

    task_id = '7ab75263-7667-480b-8afe-5611055c1b91'
    with db() as session:
        task = session.get(AnalyzeRequest, task_id)

    # zip_path = ext.download(task.origin_ndvi_data, task_id)
    # extracted = ext.extract(zip_path, task_id)


    extracted = '/Users/kkorionkk/PycharmProjects/agriculture_analysis/worker/zips/7ab75263-7667-480b-8afe-5611055c1b91'
    ndvi.analyze(extracted, task)

def test_extract():
    path = '/Users/kkorionkk/Downloads/archive (1)/Archive.zip'
    ext = Extractor()
    return ext.extract(path, 'huihui')
    # ext.delete_dir('/Users/kkorionkk/PycharmProjects/agriculture_analysis/worker/zips/huihui')

if __name__ == "__main__":
    test()
