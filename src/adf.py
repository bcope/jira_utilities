from utils import get_logger


_LOGGER = get_logger(__name__, info=True)


class ADF:
    """Class to help wrap and unwrap content in appropriate Atlassian Document Format nodes
    API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/structure/
    """

    @staticmethod
    def adf_doc(content_list=[]):
        """Returns a `doc` node containing passed in content
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/doc/
        """
        invalid_types_present = [i['type'] for i in content_list if i['type'] not in [
            # valid types
            'blockquote', 'bulletList', 'codeBlock', 'heading', 'mediaGroup', 
            'mediaSingle', 'orderedList', 'panel', 'paragraph', 'rule', 'table',
        ]]
        if invalid_types_present:
            _LOGGER.error(f"doc nodes may not have any of the following as children nodes: {invalid_types_present}")
            return None
        return {
            'version': 1,
            'type': 'doc',
            'content': content_list
        }

    @staticmethod
    def adf_heading(text='', level=1):
        """Returns a `heading` node
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/heading/
        """
        return {
            'type': 'heading',
            'attrs': {
                'level': level
            },
            'content': [
                {
                    'type': 'text',
                    'text': text
                }
            ]
        }

    @staticmethod
    def adf_paragraph(content_list=[]):
        """Returns a `paragraph` node containing passed in content
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/paragraph/
        """
        # TODO: fix this
        _LOGGER.debug(f"content_list: {content_list}")
        invalid_types_present = []
        for i in content_list:
            _LOGGER.debug(f"item: {i}")
            if i['type'] not in ['emoji', 'hardBreak', 'inlineCard', 'mention', 'text']:
                invalid_types_present.append(i)
        # invalid_types_present = [i['type'] for i in content_list if i['type'] not in [
        #     # valid types
        #     'emoji', 'hardBreak', 'inlineCard', 'mention', 'text',
        # ]]
        if invalid_types_present:
            _LOGGER.error(f"paragraph nodes may not have any of the following as children nodes: {invalid_types_present}")
            return None
        return {
            'type': 'paragraph',
            'content': content_list
        }

    @staticmethod
    def adf_text(text=''):
        """Returns a `text` node
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/text/
        """
        return {
            'type': 'text',
            'text': text,
        }

    @staticmethod
    def adf_br():
        """Returns a `hardBreak` node
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/hardBreak/
        """
        return {
            'type': 'hardBreak'
        }

    @staticmethod
    def adf_table(content_list=[]):
        """Returns a `table` node
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table/
        """
        invalid_types_present = [i['type'] for i in content_list if i['type'] not in [
            # valid types
            'tableRow',
        ]]
        if invalid_types_present:
            _LOGGER.error(
                f"table nodes may not have any of the following as children nodes: {invalid_types_present}")
            return None
        return {
            'type': 'table',
            'attrs': {
                'isNumberColumnEnabled': False,
                'layout': 'default'
            },
            'content': content_list
        }

    @staticmethod
    def adf_table_row(content_list=[]):
        """Returns a `tableRow` node
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_row/
        """
        invalid_types_present = [i['type'] for i in content_list if i['type'] not in [
            # valid types
            'tableHeader', 'tableCell',
        ]]
        if invalid_types_present:
            _LOGGER.error(
                f"tableRow nodes may not have any of the following as children nodes: {invalid_types_present}")
            return None
        return {
            'type': 'tableRow',
            'content': content_list
        }

    @staticmethod
    def adf_table_header(content_list=[], attrs={}):
        """Returns a `tableHeader` node
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_header/
        """
        invalid_types_present = [i['type'] for i in content_list if i['type'] not in [
            # valid types
            'blockquote', 'bulletList', 'codeBlock', 'heading', 'mediaGroup', 'orderedList',
            'panel', 'paragraph', 'rule',
        ]]
        if invalid_types_present:
            _LOGGER.error(
                f"tableHeader nodes may not have any of the following as children nodes: {invalid_types_present}")
            return None
        return {
            'type': 'tableHeader',
            # TODO: should add in some validation for this
            'attrs': attrs,
            'content': content_list
        }

    @staticmethod
    def adf_table_cell(content_list=[], attrs={}):
        """Returns a `tableCell` node
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/nodes/table_cell/
        """
        invalid_types_present = [i['type'] for i in content_list if i['type'] not in [
            # valid types
            'blockquote', 'bulletList', 'codeBlock', 'heading', 'mediaGroup', 'orderedList',
            'panel', 'paragraph', 'rule',
        ]]
        if invalid_types_present:
            _LOGGER.error(
                f"tableCell nodes may not have any of the following as children nodes: {invalid_types_present}")
            return None
        return {
            'type': 'tableCell',
            # TODO: should add in some validation for this
            'attrs': attrs,
            'content': content_list
        }

    @staticmethod
    def adf_mark(adf_text_node, mark, attr_value=None, attr_dict=None):
        """Returns a `text` node that was passed in, modified if possible.
        API Documentation: https://developer.atlassian.com/cloud/jira/platform/apis/document/marks/em/
        """
        
        if not adf_text_node['type'] == 'text':
            _LOGGER.warning(f"Cannot add {mark} mark to {adf_text_node['type']} node")
            return adf_text_node
        
        # add mark attr if it doesn't exist
        if 'marks' not in adf_text_node:
            adf_text_node['marks'] = []

        # avoid adding duplicate mark
        if mark in [i['type'] for i in adf_text_node['marks']]:
            _LOGGER.warning(f"{mark} mark already in node")
            return adf_text_node

        # avoid adding invalid combinations of marks
        if mark == 'textColor' and [i['type'] for i in adf_text_node['marks'] if i['type'] in ['code', 'link']]:
            _LOGGER.warning(f"{mark} mark cannot be combined with code or link marks")
            return adf_text_node
        if mark == 'code' and [i['type'] for i in adf_text_node['marks'] if i['type'] != 'link']:
            _LOGGER.warning(f"{mark} mark can only be combined with link marks")
            return adf_text_node
        if mark != 'link' and [i['type'] for i in adf_text_node['marks'] if i['type'] == 'code']:
            _LOGGER.warning(f"code mark can only be combined with link marks, not {mark} marks")
            return adf_text_node

        # create mark - this is sufficient for 'code', 'em', 'strike', 'strong', 'underline'
        m = {'type': mark}

        # some marks take attr values
        if mark in ['link', 'subsup', 'textColor']:
            if attr_dict:
                # NOTE: does not verify validity of this dict
                m['attrs'] = attr_dict
            elif attr_value:
                if mark == 'link':
                    # assume that the value provided is the url
                    m['attrs'] = {'href': attr_value}
                elif mark == 'subsup':
                    m['attrs'] = {'type': attr_value}
                elif mark == 'textColor':
                    m['attrs'] = {'color': attr_value}
            else:
                _LOGGER.warning(f"{mark} marks need additional values provided via attr_value or attr_dict")
                return adf_text_node
        
        adf_text_node['marks'].append(m)
        return adf_text_node

    @staticmethod
    def split_doc_by_headings(adf_doc, smallest_heading_level=1):
        """Returns a list of dictionaries with `heading` and `content` attrs both of which contain
        adf and also a `heading_text` attr which contains a string.

        Small and large here refer to the literal interger value rather than the rendered size of
        the heading. A level 1 heading is therefore considered to be the smallest possible heading.
        
        Headings of levels larger than smallest_heading_level will be treated as content, not
        headings. If smallest_heading_level is set to 3, then levels 1, 2, 3 will be treated as
        headings, and levels 4, 5, and 6 will be treated as content.

        If no headings of levels smaller than or equal to smallest_heading_level are present, all
        the content will be returned in the content attr of the sole member of a list. The heading
        attr will be None and the heading_text value will be an empty string.

        Returns an empty list if content attr is falsy.
        """

        # TODO: update all comments with consistent language about higher, lower, smaller, larger re heading levels
        content = adf_doc['content']
        if not content:
            return []

        split_content = []
        next_member = {'heading': None, 'heading_text': '', 'content': []}
        for i in range(len(content)):
            _LOGGER.debug(f"Handling: {content[i]}")
            _LOGGER.debug(f"split_content: {split_content}")
            _LOGGER.debug(f"next_member: {next_member}")
            # handle headings of specified level or higher
            if content[i]['type'] == 'heading' and content[i]['attrs']['level'] <= smallest_heading_level:
                
                _LOGGER.debug(f"Is heading of specified level or higher")
                # next member is new - set the heading of next member
                if next_member == {'heading': None, 'heading_text': '', 'content': []}:
                    _LOGGER.debug(f"Next member is new")
                    next_member['heading'] = content[i]
                    next_member['heading_text'] = content[i]['content'][0]['text']
                    # handle last item - iterate
                    if i == len(content) - 1:
                        _LOGGER.debug(f"Handle last item - Iterate")
                        split_content.append(next_member)
                    continue
                # next member already has a heading or content - iterate - and then set the heading of next member
                elif next_member['heading'] or next_member['content']:
                    _LOGGER.debug(f"Next member already has a heading")
                    _LOGGER.debug(f"Iterate")
                    split_content.append(next_member)
                    next_member = {
                        'heading': content[i],
                        'heading_text': content[i]['content'][0]['text'],
                        'content': []
                    }
                    # handle last item - iterate
                    if i == len(content) - 1:
                        _LOGGER.debug(f"Handle last item - Iterate")
                        split_content.append(next_member)
                    continue
                else:
                    _LOGGER.debug(f"Not handling this case")
            
            # handle non-headings or headings smaller than the threshold
            else:
                _LOGGER.debug(f"Is not heading or is smaller than specified level")
                next_member['content'].append(content[i])
                # handle last item - iterate
                if i == len(content) - 1:
                    _LOGGER.debug(f"Handle last item - Iterate")
                    split_content.append(next_member)

        return split_content

    @classmethod
    def adf_node_is_empty(cls, adf_node):
        """Establish a truthy/falsy value for any instance of an ADF node.
        hardBreak and rule nodes are falsy.
        Tables without content are falsy, but column headers count as content.
        """
        # inline nodes
        if adf_node['type'] in ['emoji', 'inlineCard', 'mention']:
            return False
        if adf_node['type'] == 'hardBreak':
            return True
        if adf_node['type'] == 'text':
            return False if adf_node['text'] else True

        # child nodes
        if adf_node['type'] in ['media']:
            return False

        # top level nodes
        if adf_node['type'] == 'heading':
            return False if adf_node['content'][0]['text'] else True
        if adf_node['type'] == 'rule':
            return True
        
        # recursion required
        if adf_node['type'] in [
            'blockquote', 'bulletList', 'codeBlock', 'doc', 'listItem', 'mediaGroup', 'mediaSingle',
            'orderedList', 'panel', 'paragraph', 'table', 'tableCell', 'tableHeader', 'tableRow'
        ]:
            if not adf_node['content']:
                return True
            else:
                non_empty_nodes = [i for i in adf_node['content'] if not cls.adf_node_is_empty(i)]
                return False if non_empty_nodes else True

    @classmethod
    def get_adf_comment_from_text(cls, text):
        return cls.adf_doc(content_list=[cls.adf_paragraph(content_list=[cls.adf_text(text=text)])])

    @classmethod
    def convert_text_to_adf_paragraph(cls, text):
        if text:
            return cls.adf_paragraph(content_list=[cls.adf_text(text=text)])
        # empty text nodes blow up tableCell validity - choosing to manage that here
        else:
            return cls.adf_paragraph()

    @classmethod
    def convert_dateframe_to_adf(cls, df):
        _LOGGER.warning(
            f"This function (ADF.convert_dateframe_to_adf) is brittle and will likely break if large or irregular DataFrames are passed in.")
        # adf content list
        t_content_list = []
        # get columns
        columns = df.columns.to_list()
        tr_headers = [cls.adf_table_header(content_list=[cls.convert_text_to_adf_paragraph(str(c))])
            for c in columns
        ]
        t_content_list.append(cls.adf_table_row(content_list=tr_headers))
        # convert all data to strings
        df_str = df.astype(str)
        # convert each df row to adf
        # TODO: compare with `for i in range(df_str.index.stop):`
        for i in range(len(df_str.index)):
            # convert each cell in a df row to adf
            tr_i = [cls.adf_table_cell(content_list=[cls.convert_text_to_adf_paragraph(c)])
                for c in df_str.loc[df_str.index[i]]
            ]
            # wrap in row adf and add to list
            t_content_list.append(cls.adf_table_row(content_list=tr_i))
        t = cls.adf_table(content_list=t_content_list)
        return t

    @classmethod
    def construct_adf_comment_with_dataframe(
        cls,
        df,
        heading=None,
        heading_level=1,
        pre_table_text=None,
        post_table_text=None
    ):
        adf_content = []
        if heading:
            adf_content.append(cls.adf_heading(text=heading, level=heading_level))
        if pre_table_text:
            adf_content.append(cls.convert_text_to_adf_paragraph(pre_table_text))
        adf_content.append(cls.convert_dateframe_to_adf(df))
        if post_table_text:
            adf_content.append(cls.convert_text_to_adf_paragraph(post_table_text))
        return cls.adf_doc(content_list=adf_content)


if __name__ == '__main__':
    pass
