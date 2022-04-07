from typing import Optional
from bs4 import BeautifulSoup
from bs4.element import PageElement, Tag

def assert_is_tag_after_find(element: PageElement) -> Tag:
	assert isinstance(element, Tag), 'Unexpected:  Find called with a class returned '\
	                                 'something other than a tag looking for a class'
	return element

def find_tag(base: Tag, class_: str) -> Optional[Tag]:
	result = base.find(class_ = class_)
	if result is None:
		return result
	else:
		return assert_is_tag_after_find(result)

def clean(html: str) -> str:
	soup = BeautifulSoup(html, 'html.parser')

	# Find the main element
	ltx_main = find_tag(soup, 'ltx_page_main')
	assert ltx_main is not None, "Bad HTML:  LaTeX page doesn't contain a main element "\
								 "(ltx_page_main).  Are you sure this is a LaTeX html page "\
								 "rendered with tex2html?"

	# Add a new section to contain the footnotes
	footnote_section = soup.new_tag('section')
	ltx_main.append(footnote_section)

	for footnote_wrapper in soup.find_all(class_ = 'ltx_note'):

		footnote_wrapper = assert_is_tag_after_find(footnote_wrapper)

		# Find the content element (that's the box with the text that the footnote refers to)
		note_content = find_tag(footnote_wrapper, 'ltx_note_content')
		assert note_content is not None, 'Bad HTML:  Footnote exists without any content '\
										 'element (ltx_note_content)'

		# Find the mark in the content and remove it.  We'll replace it with our own later
		note_mark = find_tag(note_content, class_='ltx_note_mark')
		assert note_mark is not None, 'Bad HTML:  ltx_note (footnote) object without an ' \
									  'ltx_note_mark (superscript number denoting the ' \
									  'footnote number) present in the note content '\
									  '(ltx_note_content)'
		note_mark = note_mark.extract()

		# Find the note number
		note_number_raw = note_mark.string
		assert note_number_raw is not None, 'Bad HTML:  ltx_note_mark is present in a ' \
											'footnote, but is empty'
		try:
			note_number = int(note_number_raw)
		except ValueError:
			raise RuntimeError('Bad HTML:  ltx_note_mark is present in a footnote, but '\
							   'contains a non-numeric footnote number')

		# Replace the old footnote with just a reference to the new footnote
		new_reference = soup.new_tag(
			'a',
			href=f'#fn-{note_number}',
			id=f'fn-ref-{note_number}',
		)
		new_reference['class'] = 'footnote-ref'
		new_reference.string = str(note_number)
		footnote_wrapper.insert_before(new_reference)
		footnote_wrapper = footnote_wrapper.extract()

		# Build the actual footnote the reference is pointing to
		new_content = soup.new_tag('p', id = f'fn-{note_number}')
		new_content['class'] = 'footnote'
		backlink = soup.new_tag(
			'a',
			href=f'#fn-ref-{note_number}',
		)
		backlink['class'] = 'footnote-ref'
		backlink.string = str(note_number)
		new_content.contents.append(backlink)
		new_content.contents.extend(note_content.contents)
		footnote_section.append(new_content)

	return str(soup)
