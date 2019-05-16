using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WebScrapingPudelekPL.Classes
{
    public class RelatedArticle
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }

        [StringLength(2500)]
        public string Text { get; set; }

        [StringLength(2500)]
        public string Url { get; set; }
    }
}
