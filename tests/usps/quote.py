import unittest
import urllib.parse
from unittest.mock import patch
from tests.usps.fixture import proxy
from gds_helpers import to_dict, to_xml, export, jsonify
from purplship.domain.Types import RateRequest
from pyusps.ratev4request import RateV4Request
from pyusps.intlratev2request import IntlRateV2Request
from tests.utils import strip


class TestUSPSQuote(unittest.TestCase):
    def setUp(self):
        self.RateRequest = RateV4Request()
        self.RateRequest.build(to_xml(RATE_REQUEST_STR))
        self.IntlRateRequest = IntlRateV2Request()
        self.IntlRateRequest.build(to_xml(INTL_RATE_REQUEST_STR))

    def test_create_quote_request(self):
        payload = RateRequest(**RATE_PAYLOAD)

        rate_request = proxy.mapper.create_quote_request(payload)
        self.assertEqual(strip(export(rate_request)), strip(RATE_REQUEST_STR))

    def test_create_intl_quote_request(self):
        payload = RateRequest(**INTL_RATE_PAYLOAD)

        rate_request = proxy.mapper.create_quote_request(payload)
        self.assertEqual(strip(export(rate_request)), strip(INTL_RATE_REQUEST_STR))

    @patch("purplship.mappers.usps.usps_proxy.http", return_value="<a></a>")
    @patch("urllib.parse.urlencode", return_value="")
    def test_get_quotes(self, encode_mock, http_mock):
        proxy.get_quotes(self.RateRequest)

        data = encode_mock.call_args[0][0]
        self.assertEqual(strip(jsonify(data)), strip(jsonify(RATE_REQUEST)))

    @patch("purplship.mappers.usps.usps_proxy.http", return_value="<a></a>")
    @patch("urllib.parse.urlencode", return_value="")
    def test_get_intl_quotes(self, encode_mock, http_mock):
        proxy.get_quotes(self.IntlRateRequest)

        data = encode_mock.call_args[0][0]
        self.assertEqual(strip(jsonify(data)), strip(jsonify(INTL_RATE_REQUEST)))

    def test_parse_quote_response(self):
        parsed_response = proxy.mapper.parse_quote_response(to_xml(RATE_RESPONSE))
        self.assertEqual(to_dict(parsed_response), PARSED_RATE_RESPONSE)

    def test_parse_intl_quote_response(self):
        parsed_response = proxy.mapper.parse_quote_response(to_xml(INTL_RATE_RESPONSE))
        self.assertEqual(to_dict(parsed_response), PARSED_INTL_RATE_RESPONSE)

    def test_parse_quote_response_errors(self):
        parsed_response = proxy.mapper.parse_quote_response(to_xml(ERRORS))
        self.assertEqual(to_dict(parsed_response), PARSED_ERRORS)


if __name__ == "__main__":
    unittest.main()


RATE_PAYLOAD = {
    "shipper": {"postal_code": "44106"},
    "recipient": {"postal_code": "20770"},
    "shipment": {
        "dimension_unit": "IN",
        "items": [
            {
                "id": "1ST",
                "weight": 3.123_456_78,
                "packaging_type": "SM",
                "extra": {"services": ["First_Class"]},
            },
            {
                "id": "2ND",
                "width": 15,
                "height": 15,
                "length": 30,
                "weight": 1,
                "value_amount": 1000,
                "extra": {
                    "Girth": 55,
                    "Container": "NONRECTANGULAR",
                    "services": ["Priority"],
                    "options": [{"code": "Signature_Confirmation"}],
                },
            },
            {
                "id": "3RD",
                "weight": 8,
                "extra": {
                    "services": ["All"],
                    "Size": "REGULAR",
                    "ShipDate": "2016-03-23",
                },
            },
        ],
    },
}

INTL_RATE_PAYLOAD = {
    "shipper": {"postal_code": "18701"},
    "recipient": {"postal_code": "2046", "country_code": "AU"},
    "shipment": {
        "dimension_unit": "IN",
        "date": "2016-03-24T13:15:00",
        "items": [
            {
                "id": "1ST",
                "width": 10,
                "height": 10,
                "length": 15,
                "weight": 15.123_456_78,
                "value_amount": 200,
                "packaging_type": "BOX",
                "extra": {"Girth": 0, "Size": "LARGE", "Machinable": True},
            },
            {
                "id": "2ND",
                "width": 10,
                "height": 10,
                "length": 10,
                "weight": 3.123_456_78,
                "packaging_type": "SM",
                "value_amount": 75,
                "extra": {
                    "Size": "REGULAR",
                    "options": [{"code": "Insurance_Global_Express_Guaranteed"}],
                },
            },
        ],
    },
}


PARSED_RATE_RESPONSE = [
    [
        {
            "carrier": "USPS",
            "currency": "USD",
            "extra_charges": [
                {
                    "amount": 1.3,
                    "currency": "USD",
                    "name": "Certificate_of_Mailing_Form_3665",
                },
                {"amount": 3.3, "currency": "USD", "name": "Certified_Mail"},
                {
                    "amount": 8.25,
                    "currency": "USD",
                    "name": "Certified_Mail_Restricted_Delivery",
                },
                {
                    "amount": 8.25,
                    "currency": "USD",
                    "name": "Certified_Mail_Adult_Signature_Required",
                },
                {
                    "amount": 8.25,
                    "currency": "USD",
                    "name": "Certified_Mail_Adult_Signature_Restricted_Delivery",
                },
                {"amount": 6.95, "currency": "USD", "name": "Collect_on_Delivery"},
                {
                    "amount": 11.9,
                    "currency": "USD",
                    "name": "Collect_on_Delivery_Restricted_Delivery",
                },
                {"amount": 2.1, "currency": "USD", "name": "Insurance"},
                {
                    "amount": 14.0,
                    "currency": "USD",
                    "name": "Insurance_Restricted_Delivery",
                },
                {"amount": 11.7, "currency": "USD", "name": "Registered_Mail"},
                {
                    "amount": 16.65,
                    "currency": "USD",
                    "name": "Registered_Mail_Restricted_Delivery",
                },
            ],
            "service_type": "First-Class Mail<sup>®</sup> Stamped Letter",
            "total_charge": 1.1,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "extra_charges": [
                {"amount": 5.7, "currency": "USD", "name": "Adult_Signature_Required"},
                {
                    "amount": 5.95,
                    "currency": "USD",
                    "name": "Adult_Signature_Restricted_Delivery",
                },
                {"amount": 14.05, "currency": "USD", "name": "Insurance"},
                {"amount": 2.7, "currency": "USD", "name": "Return_Receipt"},
                {"amount": 0.0, "currency": "USD", "name": "USPS_Tracking_Electronic"},
            ],
            "service_type": "Priority Mail 2-Day<sup>™</sup>",
            "total_charge": 20.7,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup>",
            "total_charge": 14.9,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Medium Flat Rate Box",
            "total_charge": 13.45,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Small Flat Rate Box",
            "total_charge": 6.8,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Large Flat Rate Box APO/FPO/DPO",
            "total_charge": 16.75,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Flat Rate Envelope",
            "total_charge": 6.45,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Legal Flat Rate Envelope",
            "total_charge": 6.45,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Padded Flat Rate Envelope",
            "total_charge": 6.8,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Gift Card Flat Rate Envelope",
            "total_charge": 6.45,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Small Flat Rate Envelope",
            "total_charge": 6.45,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Priority Mail Military<sup>™</sup> Window Flat Rate Envelope",
            "total_charge": 6.45,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Media Mail Parcel",
            "total_charge": 6.93,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "service_type": "Library Mail Parcel",
            "total_charge": 6.62,
        },
    ],
    [],
]

PARSED_INTL_RATE_RESPONSE = [
    [
        {
            "carrier": "USPS",
            "currency": "USD",
            "extra_charges": [
                {
                    "amount": 2.0,
                    "currency": "USD",
                    "name": "Insurance_Global_Express_Guaranteed",
                }
            ],
            "service_type": "Package",
            "total_charge": 211.5,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "delivery_date": "03/30/2016",
            "extra_charges": [
                {
                    "amount": 0.0,
                    "currency": "USD",
                    "name": "Insurance_Global_Express_Guaranteed",
                }
            ],
            "service_type": "Package",
            "total_charge": 158.7,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "extra_charges": [
                {
                    "amount": 0.0,
                    "currency": "USD",
                    "name": "Insurance_Global_Express_Guaranteed",
                },
                {"amount": 1.35, "currency": "USD", "name": "Certificate_of_Mailing"},
                {"amount": 3.85, "currency": "USD", "name": "Return_Receipt"},
            ],
            "service_type": "Package",
            "total_charge": 118.55,
        },
        {
            "carrier": "USPS",
            "currency": "USD",
            "extra_charges": [
                {"amount": 1.3, "currency": "USD", "name": "Certificate_of_Mailing"}
            ],
            "service_type": "Envelope",
            "total_charge": 3.64,
        },
    ],
    [],
]

PARSED_ERRORS = [
    [],
    [
        {
            "carrier": "USPS",
            "code": "-2147218040",
            "message": "Invalid International Mail Type",
        }
    ],
]


ERRORS = """<?xml version="1.0" encoding="UTF-8"?>
<Error>
    <Number>-2147218040</Number>
    <Source>IntlPostage;clsIntlPostage.CalcAllPostageDimensionsXML;IntlRateV2.ProcessRequest</Source>
    <Description>Invalid International Mail Type</Description>
    <HelpFile />
    <HelpContext>1000440</HelpContext>
</Error>
"""

RATE_REQUEST_STR = f"""<RateV4Request USERID="{proxy.client.username}">
    <Revision>2</Revision>
    <Package ID="1ST">
        <Service>First Class</Service>
        <FirstClassMailType>LETTER</FirstClassMailType>
        <ZipOrigination>44106</ZipOrigination>
        <ZipDestination>20770</ZipDestination>
        <Pounds>3</Pounds>
        <Ounces>48.</Ounces>
        <Container>SM FLAT RATE ENVELOPE</Container>
        <Size>REGULAR</Size>
    </Package>
    <Package ID="2ND">
        <Service>Priority</Service>
        <ZipOrigination>44106</ZipOrigination>
        <ZipDestination>20770</ZipDestination>
        <Pounds>1</Pounds>
        <Ounces>16.</Ounces>
        <Container>NONRECTANGULAR</Container>
        <Size>LARGE</Size>
        <Width>15</Width>
        <Length>30</Length>
        <Height>15</Height>
        <Girth>55</Girth>
        <Value>1000</Value>
        <SpecialServices>
            <SpecialService>108</SpecialService>
        </SpecialServices>
    </Package>
    <Package ID="3RD">
        <Service>All</Service>
        <ZipOrigination>44106</ZipOrigination>
        <ZipDestination>20770</ZipDestination>
        <Pounds>8</Pounds>
        <Ounces>128.</Ounces>
        <Size>REGULAR</Size>
        <ShipDate Option="PEMSH">2016-03-23</ShipDate>
    </Package>
</RateV4Request>
"""

RATE_REQUEST = {"API": "RateV4", "XML": RATE_REQUEST_STR}

INTL_RATE_REQUEST_STR = f"""<IntlRateV2Request USERID="{proxy.client.username}">
    <Revision>2</Revision>
    <Package ID="1ST">
        <Pounds>15.12345678</Pounds>
        <Ounces>241.975308479999995</Ounces>
        <Machinable>True</Machinable>
        <MailType>PACKAGE</MailType>
        <ValueOfContents>200</ValueOfContents>
        <Country>AUSTRALIA</Country>
        <Container>RECTANGULAR</Container>
        <Size>LARGE</Size>
        <Width>10</Width>
        <Length>15</Length>
        <Height>10</Height>
        <Girth>0</Girth>
        <OriginZip>18701</OriginZip>
        <AcceptanceDateTime>2016-03-24T13:15:00</AcceptanceDateTime>
        <DestinationPostalCode>2046</DestinationPostalCode>
    </Package>
    <Package ID="2ND">
        <Pounds>3.12345678</Pounds>
        <Ounces>49.975308480000002</Ounces>
        <MailType>ENVELOPE</MailType>
        <ValueOfContents>75</ValueOfContents>
        <Country>AUSTRALIA</Country>
        <Container>NONRECTANGULAR</Container>
        <Size>REGULAR</Size>
        <Width>10</Width>
        <Length>10</Length>
        <Height>10</Height>
        <OriginZip>18701</OriginZip>
        <AcceptanceDateTime>2016-03-24T13:15:00</AcceptanceDateTime>
        <DestinationPostalCode>2046</DestinationPostalCode>
        <ExtraServices>
            <ExtraService>106</ExtraService>
        </ExtraServices>
    </Package>
</IntlRateV2Request>
"""

INTL_RATE_REQUEST = {"API": "IntlRateV2", "XML": INTL_RATE_REQUEST_STR}

RATE_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<RateV4Response>
    <Package ID="1ST">
        <ZipOrigination>44106</ZipOrigination>
        <ZipDestination>20770</ZipDestination>
        <Pounds>0</Pounds>
        <Ounces>3.12345678</Ounces>
        <FirstClassMailType>LETTER</FirstClassMailType>
        <Size>REGULAR</Size>
        <Machinable>TRUE</Machinable>
        <Zone>3</Zone>
        <Postage CLASSID="0">
            <MailService>First-Class Mail&lt;sup&gt;®&lt;/sup&gt; Stamped Letter</MailService>
            <Rate>1.10</Rate>
            <SpecialServices>
                <SpecialService>
                    <ServiceID>104</ServiceID>
                    <ServiceName>Certificate of Mailing (Form 3817)</ServiceName>
                    <Available>true</Available>
                    <Price>1.30</Price>
                </SpecialService>
                <SpecialService>
                    <ServiceID>105</ServiceID>
                    <ServiceName>Certified Mail&lt;sup&gt;®&lt;/sup&gt;</ServiceName>
                    <Available>true</Available>
                    <Price>3.30</Price>
                </SpecialService>
                <SpecialService>
                    <ServiceID>170</ServiceID>
                    <ServiceName>Certified Mail&lt;sup&gt;®&lt;/sup&gt; Restricted Delivery</ServiceName>
                    <Available>true</Available>
                    <Price>8.25</Price>
                </SpecialService>
                <SpecialService>
                    <ServiceID>171</ServiceID>
                    <ServiceName>Certified Mail&lt;sup&gt;®&lt;/sup&gt; Adult Signature Required</ServiceName>
                    <Available>true</Available>
                    <Price>8.25</Price>
                </SpecialService>
                <SpecialService>
                    <ServiceID>172</ServiceID>
                    <ServiceName>Certified Mail&lt;sup&gt;®&lt;/sup&gt; Adult Signature Restricted Delivery</ServiceName>
                    <Available>true</Available>
                    <Price>8.25</Price>
                </SpecialService>
                <SpecialService>
                    <ServiceID>103</ServiceID>
                    <ServiceName>Collect on Delivery</ServiceName>
                    <Available>true</Available>
                    <Price>6.95</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                    <DueSenderRequired>false</DueSenderRequired>
                </SpecialService>
                <SpecialService>
                    <ServiceID>175</ServiceID>
                    <ServiceName>Collect on Delivery Restricted Delivery</ServiceName>
                    <Available>true</Available>
                    <Price>11.90</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                    <DueSenderRequired>false</DueSenderRequired>
                </SpecialService>
                <SpecialService>
                    <ServiceID>100</ServiceID>
                    <ServiceName>Insurance</ServiceName>
                    <Available>true</Available>
                    <Price>2.10</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                    <DueSenderRequired>false</DueSenderRequired>
                </SpecialService>
                <SpecialService>
                    <ServiceID>177</ServiceID>
                    <ServiceName>Insurance Restricted Delivery</ServiceName>
                    <Available>true</Available>
                    <Price>14.00</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                    <DueSenderRequired>false</DueSenderRequired>
                </SpecialService>
                <SpecialService>
                    <ServiceID>109</ServiceID>
                    <ServiceName>Registered Mail&lt;sup&gt;™&lt;/sup&gt;</ServiceName>
                    <Available>true</Available>
                    <Price>11.70</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                    <DueSenderRequired>false</DueSenderRequired>
                </SpecialService>
                <SpecialService>
                    <ServiceID>176</ServiceID>
                    <ServiceName>Registered Mail&lt;sup&gt;™&lt;/sup&gt; Restricted Delivery</ServiceName>
                    <Available>true</Available>
                    <Price>16.65</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                    <DueSenderRequired>false</DueSenderRequired>
                </SpecialService>
            </SpecialServices>
        </Postage>
    </Package>
    <Package ID="2ND">
        <ZipOrigination>44106</ZipOrigination>
        <ZipDestination>20770</ZipDestination>
        <Pounds>1</Pounds>
        <Ounces>8</Ounces>
        <Container>NONRECTANGULAR</Container>
        <Size>LARGE</Size>
        <Zone>3</Zone>
        <Postage CLASSID="1">
            <MailService>Priority Mail 2-Day&lt;sup&gt;™&lt;/sup&gt;</MailService>
            <Rate>20.70</Rate>
            <CommitmentDate>2016-03-28</CommitmentDate>
            <CommitmentName>2-Day</CommitmentName>
            <SpecialServices>
                <SpecialService>
                    <ServiceID>119</ServiceID>
                    <ServiceName>Adult Signature Required</ServiceName>
                    <Available>true</Available>
                    <Price>5.70</Price>
                </SpecialService>
                <SpecialService>
                    <ServiceID>120</ServiceID>
                    <ServiceName>Adult Signature Restricted Delivery</ServiceName>
                    <Available>true</Available>
                    <Price>5.95</Price>
                </SpecialService>
                <SpecialService>
                    <ServiceID>100</ServiceID>
                    <ServiceName>Insurance</ServiceName>
                    <Available>true</Available>
                    <Price>14.05</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                    <DueSenderRequired>false</DueSenderRequired>
                </SpecialService>
                <SpecialService>
                    <ServiceID>102</ServiceID>
                    <ServiceName>Return Receipt</ServiceName>
                    <Available>true</Available>
                    <Price>2.70</Price>
                </SpecialService>
                <SpecialService>
                    <ServiceID>155</ServiceID>
                    <ServiceName>USPS Tracking&lt;sup&gt;™&lt;/sup&gt; Electronic</ServiceName>
                    <Available>true</Available>
                    <Price>0.00</Price>
                </SpecialService>
            </SpecialServices>
        </Postage>
    </Package>
    <Package ID="3RD">
        <ZipOrigination>90210</ZipOrigination>
        <ZipDestination>96698</ZipDestination>
        <Pounds>8</Pounds>
        <Ounces>32</Ounces>
        <Size>REGULAR</Size>
        <Machinable>TRUE</Machinable>
        <Zone>4</Zone>
        <Postage CLASSID="1">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt;</MailService>
            <Rate>14.90</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="17">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Medium Flat Rate Box</MailService>
            <Rate>13.45</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="28">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Small Flat Rate Box</MailService>
            <Rate>6.80</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="22">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Large Flat Rate Box APO/FPO/DPO</MailService>
            <Rate>16.75</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="16">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Flat Rate Envelope</MailService>
            <Rate>6.45</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="44">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Legal Flat Rate Envelope</MailService>
            <Rate>6.45</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="29">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Padded Flat Rate Envelope</MailService>
            <Rate>6.80</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="38">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Gift Card Flat Rate Envelope</MailService>
            <Rate>6.45</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="42">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Small Flat Rate Envelope</MailService>
            <Rate>6.45</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="40">
            <MailService>Priority Mail Military&lt;sup&gt;™&lt;/sup&gt; Window Flat Rate Envelope</MailService>
            <Rate>6.45</Rate>
            <CommitmentDate />
            <CommitmentName>Military</CommitmentName>
        </Postage>
        <Postage CLASSID="6">
            <MailService>Media Mail Parcel</MailService>
            <Rate>6.93</Rate>
        </Postage>
        <Postage CLASSID="7">
            <MailService>Library Mail Parcel</MailService>
            <Rate>6.62</Rate>
        </Postage>
        <Restriction>
            <Restrictions>A1. Mail addressed to 'Any Servicemember' or similar wording such as 'Any Soldier, Sailor, Airman or Marine', 'Military Mail', etc., is prohibited. Mail must be addressed to an individual or job title, such as 'Commander', 'Commanding Officer', etc. A2. APO/FPO/DPO addresses shall not include a city and/or country name. B. When a customs declaration is required, the surface area of the address side of the item to be mailed must be large enough to contain completely the applicable customs declaration, postage, and any applicable markings, endorsements, and extra service labels. Customs declarations forms required for use to or from APO/FPO/DPO addresses are as follows: B. a. Priority Mail Express mailpieces must bear PS Form 2976-B. B. b. For other mail classes, mailpieces must bear PS Form 2976 (or, if the customer prefers, a PS Form 2976-A) if the mailpiece weighs 16 ounces or more, or contains goods. The following exceptions apply: B. a. Known mailers are exempt from providing customs documentation on non-dutiable letters, and printed matter weighing 16 ounces or more. A known mailer is a business mailer who enters volume mailings through a business mail entry unit (BMEU) or other bulk mail acceptance location, pays postage through an advance deposit account, uses a permit imprint for postage payment, and submits a completed postage statement at the time of entry that certifies the mailpieces contain no dangerous materials that are prohibited by postal regulations. B. b. All federal, state, and local government agencies whose mailings are regarded as "Official Mail" are exempt from providing customs documentation on mail addressed to an APO, FPO, or DPO except for those to which restriction "B2" applies. B. c. Prepaid mail from military contractors is exempt, providing the mailpiece is endorsed "Contents for Official Use - Exempt from Customs Requirements." V. Priority Mail Express Military Service (PMEMS) not available from any origin.</Restrictions>
        </Restriction>
    </Package>
</RateV4Response>
"""

INTL_RATE_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<IntlRateV2Response>
    <Package ID="1ST">
        <Prohibitions>Coins; bank notes; currency notes (paper money); securities of any kind payable to bearer; traveler's checks; platinum, gold, and silver (except for jewelry items meeting the requirement in "Restrictions" below); precious stones (except when contained in jewelry items meeting the requirement in "Restrictions" below); and other valuable articles are prohibited. Fruit cartons (used or new). Goods bearing the name "Anzac." Goods produced wholly or partly in prisons or by convict labor. Most food, plant, and animal products, including the use of products such as straw and other plant material as packing materials. Perishable infectious biological substances. Radioactive materials. Registered philatelic articles with fictitious addresses. Seditious literature. Silencers for firearms. Used bedding.</Prohibitions>
        <Restrictions>Jewelry is permitted only when sent as an insured parcel using Priority Mail International service. In addition, Australian Customs regulations prohibit importation of jewelry that is made with ivory or from endangered species, such as snake, elephant, or crocodile, that does not have an accompanying Import/Export Permit in relation to the Convention on International Trade in Endangered Species of Wild Fauna and Flora (CITES). Meat and other animal products; powdered or concentrated milk; and other dairy products requires permission to import from the Australian quarantine authorities. Permission of the Australian Director-General of Health is required to import medicines.</Restrictions>
        <Observations>Duty may be levied on catalogs, price lists, circulars, and all advertising introduced into Australia through the mail, regardless of the class of mail used.</Observations>
        <CustomsForms>First-Class Mail International items and Priority Mail International Flat Rate Envelopes and Small Flat Rate Boxes: PS Form 2976 (see 123.61) Priority Mail International parcels: PS Form 2976-A inside 2976-E (envelope)</CustomsForms>
        <ExpressMail>Country Code: AU Reciprocal Service Name: Express Post Required Customs Form/Endorsement 1. Business and commercial papers. No form required. Endorse item clearly next to mailing label as BUSINESS PAPERS. 2. Merchandise samples without commercial value microfilm, microfiche, and computer data. PS Form 2976-B placed inside PS Form 2976-E (plastic envelope). 3. Merchandise and all articles subject to customs duty. PS Form 2976-B placed inside PS Form 2976-E (plastic envelope). Note: 1. Coins; banknotes; currency notes, including paper money; securities of any kind payable to bearer; traveler's checks; platinum, gold, and silver; precious stones; jewelry; watches; and other valuable articles are prohibited in Priority Mail Express International shipments to Australia. 2. Priority Mail Express International With Guarantee service - which offers a date-certain, postage-refund guarantee - is available to Australia. Areas Served: All except Lord Howe Island and the Australian Antarctic territories.</ExpressMail>
        <AreasServed>Please reference Express Mail for Areas Served.</AreasServed>
        <AdditionalRestrictions>No Additional Restrictions Data found.</AdditionalRestrictions>
        <Service ID="12">
            <Pounds>15</Pounds>
            <Ounces>0</Ounces>
            <Machinable>true</Machinable>
            <MailType>Package</MailType>
            <Container>RECTANGULAR</Container>
            <Size>LARGE</Size>
            <Width>10</Width>
            <Length>15</Length>
            <Height>10</Height>
            <Girth>0</Girth>
            <Country>AUSTRALIA</Country>
            <Postage>211.50</Postage>
            <ExtraServices>
                <ExtraService>
                    <ServiceID>106</ServiceID>
                    <ServiceName>Insurance</ServiceName>
                    <Available>true</Available>
                    <Price>2.00</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                </ExtraService>
            </ExtraServices>
            <ValueOfContents>200.00</ValueOfContents>
            <SvcCommitments>1 - 3 business days to many major markets</SvcCommitments>
            <SvcDescription>USPS GXG&lt;sup&gt;™&lt;/sup&gt; Envelopes</SvcDescription>
            <MaxDimensions>USPS-Produced regular size cardboard envelope (12-1/2" x 9-1/2"), the legal-sized cardboard envelope (15" x 9-1/2") and the GXG Tyvek envelope (15-1/2" x 12-1/2")</MaxDimensions>
            <MaxWeight>70</MaxWeight>
            <GXGLocations>
                <PostOffice>
                    <Name>WILKES BARRE PDC</Name>
                    <Address>300 S MAIN ST</Address>
                    <City>WILKES BARRE</City>
                    <State>PA</State>
                    <ZipCode>18701</ZipCode>
                    <RetailGXGCutOffTime>5:00 PM</RetailGXGCutOffTime>
                    <SaturDayCutOffTime>2:00 PM</SaturDayCutOffTime>
                </PostOffice>
            </GXGLocations>
        </Service>
        <Service ID="1">
            <Pounds>15</Pounds>
            <Ounces>0</Ounces>
            <Machinable>true</Machinable>
            <MailType>Package</MailType>
            <Container>RECTANGULAR</Container>
            <Size>LARGE</Size>
            <Width>10</Width>
            <Length>15</Length>
            <Height>10</Height>
            <Girth>0</Girth>
            <Country>AUSTRALIA</Country>
            <Postage>158.70</Postage>
            <ExtraServices>
                <ExtraService>
                    <ServiceID>106</ServiceID>
                    <ServiceName>Insurance</ServiceName>
                    <Available>true</Available>
                    <Price>0.00</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                </ExtraService>
            </ExtraServices>
            <ValueOfContents>200.00</ValueOfContents>
            <SvcCommitments>Wed, Mar 30, 2016 Guaranteed</SvcCommitments>
            <SvcDescription>Priority Mail Express International&lt;sup&gt;™&lt;/sup&gt;</SvcDescription>
            <MaxDimensions>Max. length 36", max. length plus girth 97"</MaxDimensions>
            <MaxWeight>66</MaxWeight>
            <GuaranteeAvailability>03/30/2016</GuaranteeAvailability>
        </Service>
        <Service ID="2">
            <Pounds>15</Pounds>
            <Ounces>0</Ounces>
            <Machinable>true</Machinable>
            <MailType>Package</MailType>
            <Container>RECTANGULAR</Container>
            <Size>LARGE</Size>
            <Width>10</Width>
            <Length>15</Length>
            <Height>10</Height>
            <Girth>0</Girth>
            <Country>AUSTRALIA</Country>
            <Postage>118.55</Postage>
            <ExtraServices>
                <ExtraService>
                    <ServiceID>106</ServiceID>
                    <ServiceName>Insurance</ServiceName>
                    <Available>true</Available>
                    <Price>0.00</Price>
                    <DeclaredValueRequired>true</DeclaredValueRequired>
                </ExtraService>
                <ExtraService>
                    <ServiceID>100</ServiceID>
                    <ServiceName>Certificate of Mailing</ServiceName>
                    <Available>true</Available>
                    <Price>1.35</Price>
                </ExtraService>
                <ExtraService>
                    <ServiceID>105</ServiceID>
                    <ServiceName>Return Receipt</ServiceName>
                    <Available>true</Available>
                    <Price>3.85</Price>
                </ExtraService>
            </ExtraServices>
            <ValueOfContents>200.00</ValueOfContents>
            <SvcCommitments>6 - 10 business days to many major markets</SvcCommitments>
            <SvcDescription>Priority Mail International&lt;sup&gt;®&lt;/sup&gt;</SvcDescription>
            <MaxDimensions>Max. length 42", max. length plus girth 97"</MaxDimensions>
            <MaxWeight>66</MaxWeight>
        </Service>
    </Package>
    <Package ID="2ND">
        <Prohibitions>Articles made of tortoise-shell, mother of pearl, ivory, bone meerschaum and amber (succin), natural or reconstructed, worked jade and mineral substances similar to jade. Canned vegetables, fish, plums and nuts. Funeral urns. Household articles made of tin. Perishable infectious biological substances. Perishable noninfectious biological substances. Pictures and printed matter of pornographic or immoral nature, or which tend to incite crime or juvenile delinquency. Radioactive materials. Saccharine in tablets or packets. Used clothing, accessories, blankets, linen, textile furnishings, footwear and headwear. Watches and clocks.</Prohibitions>
        <Restrictions>Articles of gold or platinum, jewelry and precious stones must be licensed by the Algerian Ministry of Finance. Coins, banknotes, negotiable securities, checks and other instruments of payment, may only be imported by the Central Bank of Algeria or approved intermediary banks. Medicines for human or veterinary use, dietetic products, serums, vaccines and similar produce; medical, surgical, and dental instruments and prostheses require prior approval from the Ministry of Public Health and subject to the visa of the Central Algerian Pharmacy.</Restrictions>
        <Observations>Import permits or licenses are required for many types of goods; therefore, the sender should ascertain from the addressee before mailing whether the necessary documents are held.</Observations>
        <CustomsForms>First-Class Mail International items and Priority Mail International Flat Rate Envelopes and Small Flat Rate Boxes: PS Form 2976 (see 123.61) Priority Mail International parcels: PS Form 2976-A inside 2976-E (envelope)</CustomsForms>
        <ExpressMail>Country Code: DZ Reciprocal Service Name: EMS Required Customs Form/Endorsement 1. Correspondence and business papers. PS Form 2976-B placed inside PS Form 2976-E (plastic envelope). Endorse item clearly next to mailing label as BUSINESS PAPERS. 2. Merchandise samples without commercial value and not subject to customs duty. PS Form 2976-B placed inside PS Form 2976-E (plastic envelope). 3. Merchandise and all articles subject to customs duty. PS Form 2976-B placed inside PS Form 2976-E (plastic envelope). Include a commercial invoice in each item. Note: Coins; banknotes; currency notes, including paper money; securities of any kind payable to bearer; traveler's checks; platinum, gold, and silver; precious stones; jewelry; watches; and other valuable articles are prohibited in Priority Mail Express International shipments. All items prohibited in regular international mail are also prohibited in Priority Mail Express International to Algeria. Areas Served: See the following list for areas served. Adrar RP Ain Benian Ain Defla RP Ain Smara Ain Temouchent RP Alger aeroport Priority Mail Express International Alger Didouche Mourad Alger RP Algiers and suburbs, as well as all main towns of Wilaya (department) Annaba aeroport Priority Mail Express International Annaba Amirouche Annaba-Menadia Annaba RP Arzew Batna RP Bechar RP Bejaia RP Berrahal (Annaba) Bilda RP Biskra RP Bordj Bou Arreridj RP Bordj Bounaam Bouira RP Bou Ismail Boumerdes RP Cheraga Chlef RP Constantine aeroport Priority Mail Express International Constentine Daksi Constantine RP Constantine Sidi Mabrouk Dar El Beida Didouche Mourad Djelfa RP Douera El Attaf El Bayadh RP El-Biar El Hadjar (Annaba) El Harrach El Khroub El Khroub Djeffal Amar El Madania El Oued RP El Tarf RP Fouka Ghardaia RP Guelma RP Haasi Messaoud Hadjout Haidra Hamma Bouziane Hussein-Dey In Amenas Jijel RP Kais Khemisti Khenchela RP Kolea Kouba Laghouat RP Lardjen Layoune Mascara RP Medea RP Mila RP Mostaganem RP MSila RP Naama RP Oran Oran aeroport Priority Mail Express International Oum El Bouaghi RP Relizane RP Rouiba Saida RP Setif RP Sidi Bel Abbes-Sidi Yacine Skikda RP Souk Ahras RP Staoueli Tamanrasset RP Tebessa RP Theniet El Had Tiaret RP Tindouf RP Tipaza RP Tissemsilt RP Tizi Ouzou RP Tlemcen RP Zeralda Zighout Youcef</ExpressMail>
        <AreasServed>Please reference Express Mail for Areas Served.</AreasServed>
        <AdditionalRestrictions>No Additional Restrictions Data found.</AdditionalRestrictions>
        <Service ID="13">
            <Pounds>0</Pounds>
            <Ounces>3.12345678</Ounces>
            <MailType>Envelope</MailType>
            <Container />
            <Size>REGULAR</Size>
            <Width>0.0</Width>
            <Length>0.0</Length>
            <Height>0.0</Height>
            <Girth>0.0</Girth>
            <Country>ALGERIA</Country>
            <Postage>3.64</Postage>
            <ExtraServices>
                <ExtraService>
                    <ServiceID>100</ServiceID>
                    <ServiceName>Certificate of Mailing</ServiceName>
                    <Available>true</Available>
                    <Price>1.30</Price>
                </ExtraService>
            </ExtraServices>
            <ValueOfContents>75.00</ValueOfContents>
            <InsComment>SERVICE</InsComment>
            <SvcCommitments>Varies by destination</SvcCommitments>
            <SvcDescription>First-Class Mail&lt;sup&gt;®&lt;/sup&gt; International Letter</SvcDescription>
            <MaxDimensions>Max. length 11-1/2", height 6-1/8" or thickness 1/4"</MaxDimensions>
            <MaxWeight>.22</MaxWeight>
        </Service>
    </Package>
</IntlRateV2Response>
"""
