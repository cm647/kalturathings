"""
This script is intended to transform csv metadata in xml for upload to Kaltura's KMC batch uploader.
It suits only basic fields, and is intended to create "draft entries" (entries withot media attached at the time of upload)
It's stupidly redundant in part because the order of subfields matters for kaltura performance.


Needs: absolute path to file input (takes utf8 csv)
returns: kaltura batch xml (returns it to the same folder as the csv)
"""
import argparse
import csv
import os
import sys
import re
import xml.etree.ElementTree as xml


fields = {
        'referenceId' : 'referenceId',
        'title' : 'name',
        'description' : 'description',
        'tags' : 'tags',
        'category' : 'categories',
        'contentType' : 'mediaType',
        'metadataProfileId' : '5761',
        'metadataField_Identifier' : 'Identifier',
        'metadataField_Collection' : 'Collection',
        'metadataField_AccessionNumber' : 'AccessionNumber',
        'metadataField_Repository' : 'Repository',
        'metadataField_AccessLevel' : 'AccessLevel',
        'metadataField_ASpaceIdentifier' : 'ASpaceIdentifier'
        }

audioFileExt = ['mp3', 'aiff', 'mp4', 'wav', 'au', 'mid', 'midi', 'ogg','flac',
                'm4a', 'aac', 'aif', 'aifc', 'snd', 'ra', 'rm', 'ram', 'wma',
                'm4p', 'wav']


def makeXML(reader, outputFileName):
    print('making xml')
    # kaltura = xml.Element('mrss') #make root
    # xml.register_namespace('xmlns:xsd', 'http://www.w3.org/2001/XMLSchema') #add namespaces
    # xml.register_namespace('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')#add namespaces
    # xml.register_namespace('xsi:noNamespaceSchemaLocation', 'ingestion.xsd')#add namespaces
    kaltura = xml.Element('mrss', attrib={'xmlns:xsd' : 'http://www.w3.org/2001/XMLSchema',
                                'xmlns:xsi' : 'http://www.w3.org/2001/XMLSchema-instance',
                                'xsi:noNamespaceSchemaLocation' : 'ingestion.xsd'})
    # add subelement "channel"
    chl = xml.SubElement(kaltura, 'channel')
    for row in reader:
        # add subelement "item" per row
        item = xml.SubElement(chl, 'item')
        action = xml.SubElement(item, 'action')
        action.text = "add"
        type = xml.SubElement(item, 'type')
        type.text = "1"
        referenceId = xml.SubElement(item, 'referenceId')
        name = xml.SubElement(item, 'name')
        description = xml.SubElement(item, 'description')
        tags = xml.SubElement(item, 'tags')
        categories = xml.SubElement(item, 'categories')
        media = xml.SubElement(item, 'media')
        mediaType = xml.SubElement(media, 'mediaType')
        custom = xml.SubElement(item, 'customDataItems')
        customD = xml.SubElement(custom, 'customData')
        customD.set('metadataProfileId', '5761')
        xmlD = xml.SubElement(customD, 'xmlData')
        metadata = xml.SubElement(xmlD, 'metadata')
        identifier = xml.SubElement(metadata, 'Identifier')
        collection = xml.SubElement(metadata, 'Collection')
        accession = xml.SubElement(metadata, 'AccessionNumber')
        repository = xml.SubElement(metadata, 'Repository')
        accesslevel = xml.SubElement(metadata, 'AccessLevel')
        creation = xml.SubElement(metadata, 'DateOfCreation')
        aspace = xml.SubElement(metadata, 'ASpaceIdentifier')


        for rk in row.keys():
            if rk == 'referenceId': #record the reference ID as needed and reflect file type
                refID = row[rk].split('.')
                # eltmp = xml.SubElement(item, 'referenceId')
                referenceId.text = str(refID[0])
                # print(refID[1].lower())#see if it's an audio file. if not, assume video
                # if refID[1].lower() in audioFileExt:
                #     print('audio file')
                #     # eltmp=xml.SubElement(item, 'type')
                #     type.text = '2'
                # else:
                #     print('video file')
                #     # eltmp=xml.SubElement(item, 'type')
                #     type.text = '1'
            elif rk == 'tags': #normalize delimiter & create a subelement per tag

                tag = row[rk].replace(',','|').replace(';','|')
                # print(tag)
                tag = tag.split('|')
                # print(tag)
                maxloops = len(tag)
                # print(maxloops)
                occuredloops = 0
                while maxloops > occuredloops:
                    # print('17 multifield')
                    eltmp = xml.SubElement(tags, 'tag')
                    eltmp.text = str(tag[occuredloops]).strip()
                    # print('loop # ' + str(occuredloops + 1) + ' value is ' + eltmp.text)
                    occuredloops = occuredloops + 1

            elif rk == 'category':
                category = row[rk].replace(',','|').replace(';','|')
                # print(category)
                category = category.split('|')
                # print(category)
                maxloops = len(category)
                # print(maxloops)
                occuredloops = 0
                while maxloops > occuredloops:
                    # print('17 multifield')
                    eltmp = xml.SubElement(categories, 'category')
                    eltmp.text = str(category[occuredloops]).strip()
                    # print('loop # ' + str(occuredloops + 1) + ' value is ' + eltmp.text)
                    occuredloops = occuredloops + 1

            elif rk =='contentType':
                if 'ideo' in row[rk]:
                    # eltmp=xml.SubElement(item, 'type')
                    mediaType.text = '1'
                else:
                    # print('audio file')
                    # eltmp=xml.SubElement(item, 'type')
                    mediaType.text = '5'

            elif 'dentifier' in rk and not 'ASpace' in rk:
                identifier.text = str(row[rk])

            elif 'ollection' in rk:
                collection.text = str(row[rk])

            elif 'Accession' in rk:
                accession.text = str(row[rk])

            elif 'epository' in rk:
                repository.text = str(row[rk])

            elif 'Level' in rk:
                accesslevel.text = str(row[rk])

            elif 'Creation' in rk:
                creation.text = str(row[rk])

            elif 'title' in rk or 'name' in rk:
                name.text = str(row[rk])

            elif 'ASpace' in rk:
                aspace.text = str(row[rk])
                
            elif 'description' in rk:
                description.text = str(row[rk])

            # elif len(row[rk]) > 0 and not '5761' in str(row[rk]):
            #     eltmp = xml.SubElement(item, fields[rk])
            #     eltmp.text = str(row[rk])

            else:
                # print('no content in field ' + str(rk))
                pass

    md_xml = xml.ElementTree(kaltura)
    # print(str(md_xml))
    toast = md_xml.write(outputFileName, xml_declaration=True)
    # print(toast)


    return



def makereader(md):
    # print('in makereader')
    csvfile = open(md, encoding='utf-8-sig')
    reader = csv.DictReader(csvfile)
    # headers = reader.fieldnames
    # print(str(6))
    # not_mapped = set() #catch errors
    return reader


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('md', metavar='[input_metadata]',
                        help='input file that contains metadata')
    args = parser.parse_args()
    print ('metadata file = ' + args.md)
    reader = makereader(args.md)
    outputFileName = str(args.md.split('.')[0] + '.xml')
    print('outputname = ' + outputFileName)
    makeXML(reader, outputFileName)


if __name__ == "__main__":
    main()
