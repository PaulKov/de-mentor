<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:o="urn:lab:orders"
  exclude-result-prefixes="o">
  <xsl:output method="xml" indent="yes"/>
  <xsl:template match="/o:Order">
    <normalized-order id="{o:Id}" customer="{o:Customer/@id}">
      <xsl:for-each select="o:Lines/o:Line">
        <item code="{@sku}" quantity="{@qty}"/>
      </xsl:for-each>
    </normalized-order>
  </xsl:template>
</xsl:stylesheet>
