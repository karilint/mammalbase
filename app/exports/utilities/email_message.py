from datetime import date
from config.settings import SITE_DOMAIN

def generate_download_ready_message(export_id):
    """Creates an email message and download link to the exported data"""
#    export = ExportFile.objects.get(pk=export_id)
    current_date = date.today()

    # Format the date as "7th August 2023"
    formatted_date = current_date.strftime("%d %B %Y")

    # Add "th" to the day if it's between 11 and 13 to handle exceptions
    if 11 <= current_date.day <= 13:
        formatted_date = formatted_date.replace(
                str(current_date.day),
                str(current_date.day) + "th")
    else:
        # Handle other day numbers with appropriate suffixes (st, nd, rd)
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(current_date.day % 10, 'th')
        formatted_date = formatted_date.replace(
                str(current_date.day),
                str(current_date.day) + suffix)

    # Print the text with the formatted date
    print(f"Accessed {formatted_date}")

    return f"""
Dear MammalBase User,

We hope this email finds you well. We are pleased to inform you that your
requested data export from MammalBase is now ready for access. You can find
the export file using the Ecological Traitdata Standard (ETS) format at the
link provided at the end of this message.

The ETS format allows for the integration of the dataset into your research
workflow. To learn more about the ETS terminology, please visit:
https://terminologies.gfbio.org/terms/ets/pages/

At MammalBase, we remain dedicated to fostering research on mammalian traits
and measurements, continually expanding our database with the latest findings
to meet the needs of researchers like you.

As a part of our ongoing efforts to enhance the quality and scope of our
database, we welcome contributions from the research community. Should you or
your colleagues possess additional original, published trait and measurement
data on mammals, we would be grateful to include it. For further inquiries,
kindly contact Dr Kari Lintulaakso at kari.lintulaakso@helsinki.fi at the
Finnish Museum of Natural History, and he will be pleased to provide
a preformatted import template file in ETS format.

To cite the exported dataset, please include the following information:
The MammalBase community 2023. / CC BY 4.0.
http://doi.org/10.5281/zenodo.7462864
Accessed {formatted_date} at https://mammalbase.net

To access your requested data, kindly use the following link:
https://{SITE_DOMAIN}/exports/get_file/{export_id}

If you require any assistance or have inquiries about the data or our
platform, please don't hesitate to contact our dedicated Team MammalBase.

We value your participation in the MammalBase community and appreciate your
support in making this resource a valuable asset to researchers worldwide.

Best regards,

Team MammalBase
"""