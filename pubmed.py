from Bio import Entrez
from Bio import Medline
import os

# module setup stuff
Entrez.email = "team@impactstory.org"
Entrez.tool = "Impactstory"


def get_medline_records(pmids):
    handle = Entrez.efetch(db="pubmed", id=pmids, rettype="medline", retmode="text")
    records = Medline.parse(handle)
    return list(records)


def get_results_from_author_name(author_name):
    handle = Entrez.esearch(db="pubmed", term=author_name)
    result = Entrez.read(handle)
    handle.close()
    print result
    return result


def get_pmids_from_author_name(author_name):
    result = get_results_from_author_name(author_name)
    return result["IdList"]


def get_pmids_for_refset_using_mesh(pmid, mesh_term, year):
    search_string = '({mesh_term}[MeSH Major Topic]) AND "{year}"[Date - Publication]'.format(
        mesh_term=mesh_term,
        year=year
    )
    print "searching pubmed for ", search_string
    handle = Entrez.esearch(
        db="pubmed",
        term=search_string,
        retmax=10)
    record = Entrez.read(handle)
    print "found this on pubmed:", record["IdList"]
    return record["IdList"]


def explode_mesh_line(mesh_line):
    # turn foo/bar/*baz into a list of ['foo/bar', 'foo/*baz']

    terms = mesh_line.split("/")
    ret = []
    if len(terms) == 1:
        ret.append(terms[0])
    else:
        ret = []
        for qualifier in terms[1:]:
            ret.append(terms[0] + "/" + qualifier)

    return ret

def explode_all_mesh(mesh_lines_list):
    ret = []
    for mesh_line in mesh_lines_list:
        exploded_line = explode_mesh_line(mesh_line)
        ret += exploded_line

    return ret


def get_pmids_for_refset(pmid, mesh_term, year):
    related_pmids = get_related_pmids([pmid])
    second_order_related_pmids = get_related_pmids(related_pmids)
    pmids = related_pmids + second_order_related_pmids
    record = get_medline_records([pmid])
    pmids = get_filtered_by_year(pmids, year)
    return pmids


def get_related_pmids(pmids):
    # send just first few pmids, otherwise URL gets too long
    if len(pmids) > 50:
        pmids = pmids[0:50]
    # send pmids as a list of strings, not a single string, to get
    # elink call that has ids send individually
    # see https://github.com/biopython/biopython/issues/361
    # pmids_list = [str(pmid) for pmid in pmids]
    pmids_string = ",".join([str(pmid) for pmid in pmids])
    record = Entrez.read(Entrez.elink(dbfrom="pubmed", id=pmids_string))
    # print record
    related_pmids = [entry["Id"] for entry in record[0]["LinkSetDb"][0]["Link"]]
    return related_pmids


def get_second_order_related(pmid):
    related_pmids = get_related_pmids([pmid])
    if not related_pmids:
        return []
    second_order_related_pmids = get_related_pmids(related_pmids)
    return second_order_related_pmids


def get_filtered_by_year(pmids, year):
    if not pmids:
        return []

    pmids_string = ",".join([str(pmid) for pmid in pmids])
    handle = Entrez.epost(db="pubmed", id=pmids_string)
    result = Entrez.read(handle)
    handle.close()

    webenv = result["WebEnv"]
    query_key = result["QueryKey"]

    search_string = '"{year}"[Date - Publication]'.format(
        year=year)

    # add one because we'll remove the article itself, later
    RETMAX = int(os.getenv("REFSET_LENGTH", 50)) + 1

    print "searching pubmed for ", search_string

    handle = Entrez.esearch(
        db="pubmed",
        term=search_string,
        retmax=RETMAX,
        webenv=webenv, 
        query_key=query_key)
    record = Entrez.read(handle)
    handle.close()

    print "found this on pubmed:", record["IdList"]

    return record["IdList"]





