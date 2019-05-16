using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace WebScrapingPudelekPL.Classes
{
    public class Comment
    {
        [Key]
        [DatabaseGenerated(DatabaseGeneratedOption.Identity)]
        public int Id { get; set; }

        [StringLength(255)]
        public string Author { get; set; }

        public DateTime? CreatedAt { get; set; }

        [MaxLength]
        public string Message { get; set; }

        public int? ThumbsUp { get; set; }

        public int? ThumbsDown { get; set; }

        public bool? IsHighlited { get; set; }
    }
}
