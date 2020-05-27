# Make file to make things easier
MKDIR_P = mkdir -p

OUT_DIR?=results
OUT_FILE?=report-file.csv
FILE_TYPE?=csv

crawl:
	${MKDIR_P} ${OUT_DIR}
	scrapy runspider scripts/crawl.py -t $(FILE_TYPE) -o - > ${OUT_DIR}/spider-$(OUT_FILE)