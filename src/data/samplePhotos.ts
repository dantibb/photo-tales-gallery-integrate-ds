import { Photo } from "@/types/photo.types";
import mountainSunset from "@/assets/mountain-sunset.jpg";
import architectureNight from "@/assets/architecture-night.jpg";
import abstractFluid from "@/assets/abstract-fluid.jpg";
import forestPath from "@/assets/forest-path.jpg";
import oceanWaves from "@/assets/ocean-waves.jpg";
import geometricMinimal from "@/assets/geometric-minimal.jpg";

export const samplePhotos: Photo[] = [
  {
    id: "1",
    src: mountainSunset,
    title: "Golden Mountain Vista",
    summary: "A breathtaking mountain landscape captured during the magical golden hour",
    description: "This stunning landscape photograph captures the raw beauty of mountain peaks silhouetted against a dramatic golden sky. The interplay of light and shadow creates a mesmerizing scene that speaks to the soul of every nature lover. Shot during the perfect golden hour when the sun painted the clouds in vibrant oranges and pinks.",
    tags: ["landscape", "mountains", "sunset", "nature", "golden hour"],
    width: 1600,
    height: 900,
    createdAt: "2024-01-15"
  },
  {
    id: "2",
    src: architectureNight,
    title: "Urban Reflections",
    summary: "Modern architecture meets city lights in this striking urban composition",
    description: "A masterful blend of modern architectural design and urban photography. The glass facades create stunning reflections of the city lights, while the geometric patterns add depth and visual interest. This image captures the essence of contemporary urban living and the beauty found in modern design.",
    tags: ["architecture", "urban", "night", "city", "modern", "reflection"],
    width: 1200,
    height: 1600,
    createdAt: "2024-02-03"
  },
  {
    id: "3",
    src: abstractFluid,
    title: "Fluid Dreams",
    summary: "Abstract digital art featuring flowing gradients in vibrant colors",
    description: "A mesmerizing abstract composition that explores the fluidity of color and form. The flowing gradients of purple, orange, and teal create a dreamlike quality that invites contemplation. This digital artwork represents the intersection of technology and creativity, where mathematical precision meets artistic expression.",
    tags: ["abstract", "digital art", "colorful", "fluid", "gradient", "modern"],
    width: 1200,
    height: 1200,
    createdAt: "2024-02-10"
  },
  {
    id: "4",
    src: forestPath,
    title: "Woodland Serenity",
    summary: "A peaceful forest path bathed in filtered sunlight",
    description: "This tranquil forest scene captures the peaceful essence of woodland walks. Sunlight filters through the canopy, creating natural spotlights on the forest floor. The winding path invites the viewer to imagine a quiet journey through this serene natural cathedral, where every step brings a sense of calm and connection with nature.",
    tags: ["forest", "nature", "path", "trees", "peaceful", "sunlight"],
    width: 1200,
    height: 1600,
    createdAt: "2024-01-28"
  },
  {
    id: "5",
    src: oceanWaves,
    title: "Coastal Drama",
    summary: "Powerful ocean waves crash against rocky coastline at sunset",
    description: "The raw power and beauty of the ocean captured in perfect timing. Waves crash against ancient rocks while the setting sun paints the sky in brilliant colors. This seascape represents the eternal dance between water and stone, showcasing nature's incredible force and beauty in a single dramatic moment.",
    tags: ["ocean", "waves", "coast", "sunset", "rocks", "seascape", "dramatic"],
    width: 1600,
    height: 1200,
    createdAt: "2024-02-05"
  },
  {
    id: "6",
    src: geometricMinimal,
    title: "Geometric Harmony",
    summary: "Minimalist geometric patterns with soft shadows and gradients",
    description: "A study in minimalism and geometric precision. This contemporary design explores the beauty of simple forms enhanced by subtle shadows and gradients. The composition demonstrates how mathematical principles can create visually pleasing art, where less truly becomes more through careful attention to proportion and balance.",
    tags: ["geometric", "minimal", "contemporary", "design", "shadows", "patterns"],
    width: 1200,
    height: 1200,
    createdAt: "2024-02-12"
  }
];