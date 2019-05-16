using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Data.Entity;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.ComponentModel;

namespace WebScrapingPudelekPL.Classes
{
    public class Article
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }

        [StringLength(255)]
        public string Url { get; set; }

        [StringLength(500)]
        public string Title { get; set; }

        public DateTime? CreatedAt { get; set; }

        [StringLength(255)]
        public string Author { get; set; }

        [MaxLength]
        public string Content { get; set; }

        public int? NumberOfComments { get; set; }

        public int? NumberOfLikes { get; set; }

        public bool? IsDownloaded { get; set; }

        public DateTime? InsertedAt { get; set; }

        public DateTime? UpdatedAt { get; set; }

        public virtual List<Comment> Comments { get; set; }

        public virtual List<Tag> Tags { get; set; }

        public virtual List<RelatedArticle> RelatedArticles { get; set; }

    }
}
