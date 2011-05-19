#!/usr/bin/env python

""" atomize - A simple Python package for easily generating Atom feeds. """

import sys
import datetime
import codecs
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO


__package_name__ = "atomize"
__version__ = (0, 1, 0)
__author__ = "Christopher Wienberg <cwienberg@ict.usc.edu>"

__all__ = ["Feed", "Entry", "AtomError", "Author", "Category", "Content",
           "Contributor", "Generator", "Icon", "ID", "Link", "Logo",
           "Published", "Rights", "Source", "Subtitle", "Summary", "Title",
           "Updated"]


class Feed(object):

    """ Representation for an Atom feed.

    An implementation of Atom Syndication Format v1.0 """

    def __init__(self, title=None, updated=None, guid=None, author=None,
                 self_link=None, entries=[], **other_elts):

        """ Creates an Atom feed

        Required arguments:
        * title - title of the blog; may be a string or a Title object
        * updated - time the feed was updated; may be a Python datetime or an
                    Updated object
        * guid - a unique identifier for the feed; may be a string or ID object

        Potentially required arguments:
        * author - the author of the content in the feed; May be a string of
                   the author's name, an Author object, or a list of Author
                   objects (must have at least one if any entry in feed does
                   not have an Author defined; may have as many as desired)

        Highly suggested arguments:
        * self_link - the preferred URI for retrieving Atom Feed Documents
                      representing this Atom feed; may be a string of the
                      URI or a Link object with a rel attribute value of 'self'
        * entries - entries (articles, etc) that the Atom feed is delivering;
                    must be a list of Entry objects
                    (may have as many as desired)

        Optional arguments:

            List arguments; as many of these elements as desired permitted:
            * contributors - indicates a person or other entity who contributed
                             to the feed; must be a list of Contributor objects
            * categories - indicates the category/genre of the feed
            * links - any links one desires the feed to have; must be a list
                      of Link objects (no links with a rel attribute of
                      'alternate' should have the same combination of type and
                      hreflang)

            May have only one:
            * icon - A favicon for the feed; must be an Icon object
            * logo - A logo image for the feed; must be a Logo object
            * rights - A space to declare copyright information; must be a
                       Rights object
            * subtitle - A subtitle for the feed; must be a Subtitle object """

        if title is None or updated is None or guid is None:
            raise AtomError("Feed: title, updated, and guid must be defined")

        self.elements = other_elts

        if isinstance(title, basestring):
            self.elements["title"] = Title(title)
        elif isinstance(title, Title):
            self.elements["titile"] = title
        else:
            raise AtomError("Feed: title must be a string or a Title object")

        if isinstance(author, basestring):
            self.elements["authors"] = [Author(author)]
        elif isinstance(author, Author):
            self.elements["authors"] = [author]
        elif isinstance(author, list):
            self.elements["authors"] = author
        elif author is None:
            if len(entries) == 0:
                raise AtomError("Feed: not entries defined and " +
                                "no authors are defined for feed")
            for entry in entries:
                if "authors" not in entry.elements:
                    raise AtomError("Feed: not all entries have an author, " +
                                    "but no authors are defined for feed")
        else:
            raise AtomError("Feed: author must be a string, list or an " +
                            "Author object")

        if isinstance(updated, datetime.datetime):
            self.elements["updated"] = Updated(updated)
        elif isinstance(updated, Updated):
            self.elements["updated"] = updated
        else:
            raise AtomError("Feed: updated must be a datetime or an Updated " +
                            "object")

        if isinstance(self_link, basestring):
            self.elements["self_link"] = Link(self_link, rel="self",
                                              type="application/atom+xml")
        elif isinstance(self_link, Link) and self_link.rel == "self":
            self.elements["self_link"] = self_link
        elif self_link is None:
            sys.stderr.write("Warning: Feed defined without a self_link\n")
        else:
            raise AtomError("Feed: self_link must be a string or a Link " +
                            "object with a rel attribute of 'self'")

        if isinstance(guid, basestring):
            self.elements["id"] = ID(guid)
        elif isinstance(guid, ID):
            self.elements["id"] = guid
        else:
            raise AtomError("Feed: guid must be a string or an ID object")

        self.elements["generator"] = Generator(__package_name__,
                                               version="%s.%s.%s" %
                                               __version__)

        self.entries = entries

    def publish(self):

        """ Build the XML Element Tree for the feed """

        feed = ET.Element("feed")
        feed.attrib["xmlns"] = "http://www.w3.org/2005/Atom"
        for value in self.elements.values():
            if isinstance(value, list):
                for elt in value:
                    elt.publish(feed)
            else:
                value.publish(feed)

        for entry in self.entries:
            entry.publish(feed)

        return ET.ElementTree(feed)

    def _write_to_file(self, file_object, encoding):

        """ Writes the tree into the given file object """

        self.publish().write(file_object, xml_declaration=True,
                              encoding=encoding)

    def write_file(self, filename, encoding="utf-8"):

        """ Writes the Atom feed to the filename given """

        out = codecs.open(filename, "w", encoding=encoding)
        self._write_to_file(out, encoding)
        out.close()

    def feed_string(self, encoding="utf-8"):

        """ Returns a string of the Atom feed """

        feed_string = StringIO.StringIO()
        self._write_to_file(codecs.getwriter(encoding)(feed_string), encoding)
        return feed_string.getvalue()


class AtomPerson(object):

    """ Represents a person or similar entity (corp, etc).

    Allows storing the name, and optionally a uri and email address """

    def __init__(self, name, uri=None, email=None):

        """ A person entity for an Atom feed.

        Takes a name and (optionally) a uri and email address, all as strings.
        These strings will be automatically escaped. """

        self.name = name
        self.uri = uri
        self.email = email
        if uri:
            self.uri = uri
        if email:
            self.email = email

    def publish(self, parent):

        """ Used in building the Atom Feed's XML tree """

        elt = ET.SubElement(parent, self.__class__.__name__.lower())
        name = ET.SubElement(elt, "name")
        name.text = self.name
        if self.uri:
            uri = ET.SubElement(elt, "uri")
            uri.text = self.uri
        if self.email:
            email = ET.SubElement(elt, "email")
            email.text = self.email


class Author(AtomPerson):

    """ Information about the author of a feed or entry """

    pass


class Contributor(AtomPerson):

    """ Defines a person who contributed to a feed or entry """

    pass


class AtomText(object):

    """ A text object for an entry or feed """

    def __init__(self, content, content_type="text"):

        """ Initializes the text object.

        May be a regular string, html, or xhtml. If not text, the content_type
        argument must be set to 'html' or 'xhtml'. If the title is xhtml,
        an encapsulating div will automatically be included. If the title
        is html, it will be automatically escaped. """

        self.content_type = content_type
        if content_type == "text" or content_type == "html":
            self.content = content
        elif content_type == "xhtml":
            self.content = '<div>%s</div>' % content
        else:
            raise AtomError("%s: content_type must be 'text', 'html' or " +
                            "'xhtml'" % self.__class__.__name__)

    def publish(self, parent):

        """ Used in building the Atom feed's Element Tree """

        elt = ET.SubElement(parent, self.__class__.__name__.lower())
        elt.attrib["type"] = self.content_type
        if self.content_type == "xhtml":
            content_string = StringIO.StringIO()
            content_string.write(self.content)
            content_string.seek(0)
            reader = codecs.getreader("utf-8")(content_string)
            tree = ET.parse(reader, parser=ET.XMLParser(encoding="utf-8"))
            div = tree.getroot()
            div.attrib["xmlns"] = "http://www.w3.org/1999/xhtml"
            elt.append(div)
        else:
            elt.text = self.content


class Rights(AtomText):

    """ Place for a copyright definition """

    pass


class Subtitle(AtomText):

    """ A subtitle for a feed """

    pass


class Summary(AtomText):

    """ A summary of an entry.

    Should not duplicate a Content object """

    pass


class Title(AtomText):

    """ The title of the feed or an entry """

    pass


class Content(object):

    """ Contains the content of the entry """

    def __init__(self, content=None, content_type="text", src=None):

        """ Intializes the Content object.

        Unless the type is an atom media type, content must be defined. """

        try:
            if content_type == "text" or content_type == "html":
                self.content = content
            elif content_type == "xhtml":
                self.content = '<div>%s</div>' % content
        except TypeError:
            raise AtomError("Content: Must have content defined if the type " +
                            "is xhtml, html, or text")

        self.type = content_type
        self.src = src

        if src and content:
            raise AtomError("Content: Cannot have both src and content " +
                            "defined")

    def publish(self, parent):

        """ Used in building the Atom feed's XML Element Tree """

        elt = ET.SubElement(parent, "content")
        if self.content and self.type == "xhtml":
            content_string = StringIO.StringIO()
            content_string.write(self.content)
            content_string.seek(0)
            content_reader = codecs.getreader("utf-8")(content_string)
            div_tree = ET.parse(content_reader,
                                parser=ET.XMLParser(encoding="utf-8"))
            div = div_tree.getroot()
            div.attrib["xmlns"] = "http://www.w3.org/1999/xhtml"
            elt.append(div)
        elif self.content:
            elt.text = self.content
        if self.type:
            elt.attrib["type"] = self.type
        if self.src:
            elt.attrib["src"] = self.src


class AtomDate(object):

    """ A date object for an entry or feed """

    def __init__(self, date):

        """ Initializes date object.

        The date parameter must be a datetime. It is assumed to be in UTC. """

        self.date = date.strftime("%Y-%m-%dT%H:%M:%SZ")

    def publish(self, parent):

        " Used in building the Atom feed's XML Element Tree """

        elt = ET.SubElement(parent, self.__class__.__name__.lower())
        elt.text = self.date


class Updated(AtomDate):

    """ Encode information about when the entry or feed was last updated """

    pass


class Published(AtomDate):

    """ Encode information about when the entry was originally published """

    pass


class AtomURI(object):

    """ A URI object for an entry or feed """

    def __init__(self, uri):

        """ Initializes the URI object

        The uri argument must be a string and is assumed to be a proper URI."""

        self.uri = uri

    def publish(self, parent):

        """ Used in building the Atom feed's XML element tree """

        elt = ET.SubElement(parent, self.__class__.__name__.lower())
        elt.text = self.uri


class Icon(AtomURI):

    """ Allows a favicon to be defined for the Feed or Source """

    pass


class ID(AtomURI):

    """ A unique identifier for a feed or entry """

    pass


class Logo(AtomURI):

    """ Permits the definition of a logo for a feed """

    pass


class Generator(object):

    """ Information about what generated the Atom feed """

    def __init__(self, name, version=None, uri=None):

        self.name = name
        self.version = version
        self.uri = uri

    def publish(self, parent):

        """ Used in building the Atom feed's XML Element Tree """

        elt = ET.SubElement(parent, "generator")
        elt.text = self.name
        if self.version:
            elt.attrib["version"] = self.version
        if self.uri:
            elt.attrib["uri"] = self.uri


class Category(object):

    """ Information about the category of a feed or entry """

    def __init__(self, term, scheme=None, label=None):

        self.term = term
        self.scheme = scheme
        self.label = label

    def publish(self, parent):

        """ Used in building the Atom feed's XML Element Tree """

        elt = ET.SubElement(parent, "category")
        elt.attrib["term"] = self.term
        if self.scheme:
            elt.attrib["scheme"] = self.scheme
        if self.label:
            elt.attrib["label"] = self.label


class Link(object):

    """ A link for in the Atom feed """

    def __init__(self, href, rel=None, content_type=None, hreflang=None,
                 title=None, length=None):
        self.href = href
        self.rel = rel
        self.content_type = content_type
        self.hreflang = hreflang
        self.title = title
        self.length = length

    def publish(self, parent):

        """ Used in building the Atom feed's XML Element Tree """

        elt = ET.SubElement(parent, "link")
        elt.attrib["href"] = self.href
        if self.rel:
            elt.attrib["rel"] = self.rel
        if self.content_type:
            elt.attrib["type"] = self.content_type
        if self.hreflang:
            elt.attrib["hreflang"] = self.hreflang
        if self.title:
            elt.attrib["title"] = self.title
        if self.length:
            elt.attrib["length"] = self.length


class Entry(object):

    """ Defines an Atom entry (ie an article, post, etc) """

    def __init__(self, title=None, guid=None, updated=None, author=None,
                 **other_elts):

        """ Creates an Atom Entry

        Required arguments:
        * title - title of the entry; may be a string or a Title object
        * updated - time the entry was updated; may be a Python datetime or an
                    Updated object
        * guid - a unique identifier for the entry; may be a string or an ID
               object

        Potentially required arguments:
        * author - the author of the content in the entry; May be a string of
                   the author's name, an Author object, or a list of Author
                   objects (must have at least one if the feed does not have an
                   Author defined; may have as many as desired)

        Optional arguments:

            List arguments; as many of these elements as desired permitted:
            * contributors - indicates a person or other entity who contributed
                             to the entry; must be a list of Contributor
                             objects
            * categories - indicates the category/genre of the entry
            * links - any links one desires the entry to have; must be a list
                      of Link objects (no links with a rel attribute of
                      'alternate' should have the same combination of type and
                      hreflang)

            May have only one:
            * content - The content of the entry; must be a Content object
            * published - Associated with an early date in the entry's
                          life (such as publication); must be a Published
                          object
            * source - For when an entry is copied from one feed to another;
                       must be a Source object
            * rights - A space to declare copyright information; must be a
                       Rights object
            * summary - A short summary or extract from the entry; must be
                        a Summary object """

        if title is None or guid is None or updated is None:
            raise AtomError("Entry: title, guid, and updated must be defined")

        self.elements = other_elts

        if isinstance(title, basestring):
            self.elements["title"] = Title(title)
        elif isinstance(title, Title):
            self.elements["titile"] = title
        else:
            raise AtomError("Entry: title must be a string or a Title object")

        if isinstance(author, basestring):
            self.elements["authors"] = [Author(author)]
        elif isinstance(author, Author):
            self.elements["authors"] = [author]
        elif isinstance(author, list):
            self.elements["authors"] = author
        elif author is None:
            pass
        else:
            raise AtomError("Entry: author must be a string, list or an " +
                            "Author object")

        if isinstance(updated, datetime.datetime):
            self.elements["updated"] = Updated(updated)
        elif isinstance(updated, Updated):
            self.elements["updated"] = updated
        else:
            raise AtomError("Entry: updated must be a datetime or an " +
                            "Updated object")

        if isinstance(guid, basestring):
            self.elements["id"] = ID(guid)
        elif isinstance(guid, ID):
            self.elements["id"] = guid
        else:
            raise AtomError("Entry: guid must be a string or an ID object")

    def publish(self, parent):

        """ Used in building the Atom feed's XML Element Tree """

        entry = ET.SubElement(parent, "entry")
        for value in self.elements.values():
            if isinstance(value, list):
                for elt in value:
                    elt.publish(entry)
            else:
                value.publish(entry)


class Source(object):

    """ Defines an Atom source (ie an article, post, etc) """

    def __init__(self, title=None, guid=None, updated=None, author=None,
                 **other_elts):

        """ Creates an Atom source object

        Should be required arguments (but not strictly so):
        * title - title of the blog; may be a string or a Title object
        * updated - time the source was updated; may be a Python datetime or an
                    Updated object
        * guid - a unique identifier for the source; may be a string or an ID
               object

        Optional arguments:

            List arguments; as many of these elements as desired permitted:
            * author - the author of the content in the entry; Must be a list
                       of Author objects
            * contributors - indicates a person or other entity who contributed
                             to the entry; must be a list of Contributor
                             objects
            * categories - indicates the category/genre of the entry
            * links - any links one desires the entry to have; must be a list
                      of Link objects (no links with a rel attribute of
                      'alternate' should have the same combination of type and
                      hreflang)

            May have only one:
            * generator - The app that generated the source entry
            * icon - A favicon for the source entry
            * logo - A logo for the source entry
            * subtitle - A subtitle for the sourced entry/feed
            * rights - A space to declare copyright information; must be a
                       Rights object """

        if title is None or guid is None or updated is None:
            sys.stdout.write("Warning: it is recommended you define a " +
                             "title, guid, and source for a Source object\n")

        self.elements = other_elts

        if isinstance(title, basestring):
            self.elements["title"] = Title(title)
        elif isinstance(title, Title):
            self.elements["titile"] = title
        elif title is None:
            pass
        else:
            raise AtomError("Entry: title must be a string or a Title object")

        if isinstance(author, basestring):
            self.elements["authors"] = [Author(author)]
        elif isinstance(author, Author):
            self.elements["authors"] = [author]
        elif isinstance(author, list):
            self.elements["authors"] = author
        elif author is None:
            pass
        else:
            raise AtomError("Entry: author must be a string, list or an " +
                            "Author object")

        if isinstance(updated, datetime.datetime):
            self.elements["updated"] = Updated(updated)
        elif isinstance(updated, Updated):
            self.elements["updated"] = updated
        elif updated is None:
            pass
        else:
            raise AtomError("Entry: updated must be a datetime or an " +
                            "Updated object")

        if isinstance(guid, basestring):
            self.elements["id"] = ID(guid)
        elif isinstance(guid, ID):
            self.elements["id"] = guid
        elif id is None:
            pass
        else:
            raise AtomError("Entry: guid must be a string or an ID object")

    def publish(self, parent):

        """ Used in building the Atom feed's XML Element Tree """

        source = ET.SubElement(parent, "entry")
        for value in self.elements.values():
            if isinstance(value, list):
                for elt in value:
                    elt.publish(source)
            else:
                value.publish(source)


class AtomError(Exception):

    """ Errors in building the Atom feed """

    def __init__(self, msg):

        """ Initialize the message to be displayed for this error """

        self.msg = msg
        super(AtomError, self).__init__()

    def __str__(self):
        return self.msg

    def __repr__(self):
        return str(self)
