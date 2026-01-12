# Exports (Admin)

This page summarizes operational and auditing details for exports.

## Workflow overview

When a user requests an export, the system creates an export record immediately
and then processes the data asynchronously. The resulting file is attached to
the record, and a download link is emailed to the requester.

## Permissions

Users can download only their own exports. Data administrators can access any
export records in the system for support and troubleshooting.

## Auditing

Export records capture who created the request and who last modified the
record. These audit fields are set when the request is submitted, before the
background processing begins.
