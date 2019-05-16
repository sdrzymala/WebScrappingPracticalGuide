namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class migration20 : DbMigration
    {
        public override void Up()
        {
            AlterColumn("dbo.RelatedArticles", "Text", c => c.String(maxLength: 500));
        }
        
        public override void Down()
        {
            AlterColumn("dbo.RelatedArticles", "Text", c => c.String(maxLength: 255));
        }
    }
}
