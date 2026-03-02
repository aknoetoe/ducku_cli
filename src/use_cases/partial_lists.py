from typing import List
from src.core.entity import EntitiesContainer, collect_docs_entities, collect_project_entities, entities_for_comparison
from src.core.project import Project
from src.core.report import Report, IssueType
from src.helpers.comparison import fuzzy_intersection
from src.core.base_usecase import BaseUseCase

class PartialMatch(BaseUseCase):

    def __init__(self, project: Project):
        super().__init__(project)
        self.name = "partial_lists"

    def find_partials(self, project_containers: List[EntitiesContainer], docs_containers: List[EntitiesContainer], report: Report):
        '''
        This function compares 2 lists of EntitiesContainer: from project code and from documentation.
        Each containers consists of entities (strings) collected from code or docs.
        2 lists of entities are compared using fuzzy matching to find partial overlaps.
        According to certain rules, if it turns out that lists belong to the same domain,
        then it checks if some entities are missing in documentation compared to project code and
        reports it.
        '''
        seen_pairs = set()
        for e1 in project_containers:
            e1s = [str(e) for e in e1.entities]
            for e2 in docs_containers:
                e2s = [e.content for e in e2.entities]

                match = fuzzy_intersection(e1s, e2s, False)
                
                if not match:
                    continue
                
                if not match.only_a:
                    # We only care about missing items in docs compared to project code
                    continue
                
                e1_from = e1.parent + " (" + e1.type + ")"
                e2_from = e2.parent + " (" + e2.type + ")"
                
                message = f"Partial match found:\n"
                message += f" - From project: {', '.join(e1s)} {e1_from}\n"
                message += f" - From docs: {', '.join(e2s)} {e2_from}\n"
                message += f" - Missing in docs: {', '.join(match.only_a)}\n"
                message += f"Debug: {', '.join(match.matched_debug)}"

                report.add_issue(
                    message,
                    level=IssueType.WARNING,
                    project_entities=e1s,
                    project_source=e1_from,
                    docs_entities=e2s,
                    docs_source=e2_from,
                    missing_in_docs=match.only_a,
                    matched_debug=match.matched_debug
                )

    def report(self) -> Report:
        result = Report()

        files_entities = collect_project_entities(self.project)
        docs_entities = collect_docs_entities(self.project.documentation)

        unique_proj = entities_for_comparison(files_entities)
        unique_docs = entities_for_comparison(docs_entities)

        self.find_partials(unique_proj, unique_docs, result)

        return result