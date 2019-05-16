using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;
using System.Data.Entity;
using System.Linq;
using System.Reflection.Emit;
using System.Text;
using System.Threading.Tasks;

namespace WebScrapingPudelekPL.Classes
{
    public class ArticlesContext : DbContext
    {
        public ArticlesContext() : base(@"Server=demo\sql2017;Database=Pudelek;User Id=sdrzymala;Password=zaq12wsx;") { }

        public DbSet<Article> Articles { get; set; }

        public DbSet<Comment> Comments { get; set; }

        public DbSet<Tag> Tags { get; set; }

        public DbSet<RelatedArticle> RelatedArticles { get; set; }
    }
}
