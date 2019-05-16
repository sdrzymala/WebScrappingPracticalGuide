namespace WebScrapingPudelekPL.Migrations
{
    using System;
    using System.Data.Entity.Migrations;
    
    public partial class migration23 : DbMigration
    {
        public override void Up()
        {
            AlterColumn("dbo.RelatedArticles", "Url", c => c.String(maxLength: 2500));
        }
        
        public override void Down()
        {
            AlterColumn("dbo.RelatedArticles", "Url", c => c.String(maxLength: 500));
        }
    }
}
