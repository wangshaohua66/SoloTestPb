package com.colorpicker.util;

import com.colorpicker.model.ColorModel;

import java.awt.image.BufferedImage;
import java.util.*;

public class ImageColorExtractor {

    public static List<ColorModel> extractDominantColors(BufferedImage image, int numColors) {
        return extractDominantColors(image, numColors, 10);
    }

    public static List<ColorModel> extractDominantColors(BufferedImage image, int numColors, int sampleStep) {
        if (image == null || numColors <= 0) {
            return new ArrayList<>();
        }
        
        List<int[]> pixels = collectPixels(image, sampleStep);
        
        if (pixels.isEmpty()) {
            return new ArrayList<>();
        }
        
        return kMeansClustering(pixels, numColors);
    }

    public static List<ColorModel> extractColorPalette(BufferedImage image, int paletteSize) {
        return extractDominantColors(image, paletteSize);
    }

    public static Map<String, List<ColorModel>> extractByHue(BufferedImage image) {
        Map<String, List<ColorModel>> result = new LinkedHashMap<>();
        result.put("红色系", new ArrayList<>());
        result.put("黄色系", new ArrayList<>());
        result.put("绿色系", new ArrayList<>());
        result.put("青色系", new ArrayList<>());
        result.put("蓝色系", new ArrayList<>());
        result.put("品红色系", new ArrayList<>());
        result.put("中性色", new ArrayList<>());
        
        if (image == null) {
            return result;
        }
        
        List<int[]> pixels = collectPixels(image, 5);
        
        Map<Integer, Integer> colorCount = new HashMap<>();
        for (int[] pixel : pixels) {
            int rgb = (pixel[0] << 16) | (pixel[1] << 8) | pixel[2];
            colorCount.put(rgb, colorCount.getOrDefault(rgb, 0) + 1);
        }
        
        List<Map.Entry<Integer, Integer>> sortedColors = new ArrayList<>(colorCount.entrySet());
        sortedColors.sort((a, b) -> b.getValue().compareTo(a.getValue()));
        
        for (Map.Entry<Integer, Integer> entry : sortedColors) {
            int rgb = entry.getKey();
            int r = (rgb >> 16) & 0xFF;
            int g = (rgb >> 8) & 0xFF;
            int b = rgb & 0xFF;
            
            ColorModel color = new ColorModel(r, g, b);
            String category = categorizeByHue(color);
            List<ColorModel> categoryColors = result.get(category);
            
            if (categoryColors.size() < 5) {
                categoryColors.add(color);
            }
        }
        
        return result;
    }

    private static List<int[]> collectPixels(BufferedImage image, int step) {
        List<int[]> pixels = new ArrayList<>();
        int width = image.getWidth();
        int height = image.getHeight();
        
        for (int y = 0; y < height; y += step) {
            for (int x = 0; x < width; x += step) {
                int rgb = image.getRGB(x, y);
                int r = (rgb >> 16) & 0xFF;
                int g = (rgb >> 8) & 0xFF;
                int b = rgb & 0xFF;
                int a = (rgb >> 24) & 0xFF;
                
                if (a > 128) {
                    pixels.add(new int[]{r, g, b});
                }
            }
        }
        
        return pixels;
    }

    private static List<ColorModel> kMeansClustering(List<int[]> pixels, int k) {
        if (pixels.size() < k) {
            List<ColorModel> result = new ArrayList<>();
            for (int[] pixel : pixels) {
                result.add(new ColorModel(pixel[0], pixel[1], pixel[2]));
            }
            return result;
        }
        
        List<int[]> centroids = initializeCentroids(pixels, k);
        List<Integer> assignments = new ArrayList<>(Collections.nCopies(pixels.size(), 0));
        
        int maxIterations = 20;
        for (int iter = 0; iter < maxIterations; iter++) {
            boolean changed = false;
            
            for (int i = 0; i < pixels.size(); i++) {
                int[] pixel = pixels.get(i);
                int nearestCentroid = findNearestCentroid(pixel, centroids);
                if (assignments.get(i) != nearestCentroid) {
                    assignments.set(i, nearestCentroid);
                    changed = true;
                }
            }
            
            if (!changed) {
                break;
            }
            
            centroids = updateCentroids(pixels, assignments, k);
        }
        
        Map<Integer, int[]> finalCentroids = new HashMap<>();
        Map<Integer, Integer> centroidCounts = new HashMap<>();
        
        for (int i = 0; i < pixels.size(); i++) {
            int cluster = assignments.get(i);
            int[] pixel = pixels.get(i);
            
            if (!finalCentroids.containsKey(cluster)) {
                finalCentroids.put(cluster, new int[3]);
                centroidCounts.put(cluster, 0);
            }
            
            int[] sum = finalCentroids.get(cluster);
            sum[0] += pixel[0];
            sum[1] += pixel[1];
            sum[2] += pixel[2];
            centroidCounts.put(cluster, centroidCounts.get(cluster) + 1);
        }
        
        List<ColorModel> result = new ArrayList<>();
        for (int i = 0; i < k; i++) {
            if (centroidCounts.containsKey(i) && centroidCounts.get(i) > 0) {
                int[] sum = finalCentroids.get(i);
                int count = centroidCounts.get(i);
                result.add(new ColorModel(
                        sum[0] / count,
                        sum[1] / count,
                        sum[2] / count
                ));
            }
        }
        
        return result;
    }

    private static List<int[]> initializeCentroids(List<int[]> pixels, int k) {
        List<int[]> centroids = new ArrayList<>();
        Random random = new Random();
        
        List<int[]> shuffledPixels = new ArrayList<>(pixels);
        Collections.shuffle(shuffledPixels, random);
        
        for (int i = 0; i < Math.min(k, shuffledPixels.size()); i++) {
            int[] pixel = shuffledPixels.get(i);
            centroids.add(new int[]{pixel[0], pixel[1], pixel[2]});
        }
        
        return centroids;
    }

    private static int findNearestCentroid(int[] pixel, List<int[]> centroids) {
        int nearest = 0;
        double minDistance = Double.MAX_VALUE;
        
        for (int i = 0; i < centroids.size(); i++) {
            int[] centroid = centroids.get(i);
            double distance = colorDistance(pixel, centroid);
            if (distance < minDistance) {
                minDistance = distance;
                nearest = i;
            }
        }
        
        return nearest;
    }

    private static List<int[]> updateCentroids(List<int[]> pixels, List<Integer> assignments, int k) {
        List<int[]> centroids = new ArrayList<>();
        List<int[]> sums = new ArrayList<>();
        List<Integer> counts = new ArrayList<>();
        
        for (int i = 0; i < k; i++) {
            centroids.add(new int[3]);
            sums.add(new int[3]);
            counts.add(0);
        }
        
        for (int i = 0; i < pixels.size(); i++) {
            int cluster = assignments.get(i);
            int[] pixel = pixels.get(i);
            int[] sum = sums.get(cluster);
            sum[0] += pixel[0];
            sum[1] += pixel[1];
            sum[2] += pixel[2];
            counts.set(cluster, counts.get(cluster) + 1);
        }
        
        for (int i = 0; i < k; i++) {
            if (counts.get(i) > 0) {
                int[] sum = sums.get(i);
                int count = counts.get(i);
                centroids.set(i, new int[]{
                        sum[0] / count,
                        sum[1] / count,
                        sum[2] / count
                });
            }
        }
        
        return centroids;
    }

    private static double colorDistance(int[] p1, int[] p2) {
        long rmean = (p1[0] + p2[0]) / 2L;
        long r = p1[0] - p2[0];
        long g = p1[1] - p2[1];
        long b = p1[2] - p2[2];
        
        return Math.sqrt(
                (2 + rmean / 256.0) * r * r +
                4 * g * g +
                (2 + (255 - rmean) / 256.0) * b * b
        );
    }

    private static String categorizeByHue(ColorModel color) {
        int r = color.getRed();
        int g = color.getGreen();
        int b = color.getBlue();
        
        int max = Math.max(Math.max(r, g), b);
        int min = Math.min(Math.min(r, g), b);
        int chroma = max - min;
        
        if (chroma < 30) {
            return "中性色";
        }
        
        double hue;
        if (max == r) {
            hue = (g - b) / (double) chroma;
            if (hue < 0) hue += 6;
        } else if (max == g) {
            hue = (b - r) / (double) chroma + 2;
        } else {
            hue = (r - g) / (double) chroma + 4;
        }
        
        hue *= 60;
        if (hue < 0) hue += 360;
        
        if (hue < 30 || hue >= 330) {
            return "红色系";
        } else if (hue < 90) {
            return "黄色系";
        } else if (hue < 150) {
            return "绿色系";
        } else if (hue < 210) {
            return "青色系";
        } else if (hue < 270) {
            return "蓝色系";
        } else {
            return "品红色系";
        }
    }

    public static ColorModel getAverageColor(BufferedImage image) {
        if (image == null) {
            return new ColorModel(128, 128, 128);
        }
        
        int width = image.getWidth();
        int height = image.getHeight();
        long sumR = 0, sumG = 0, sumB = 0;
        int pixelCount = 0;
        
        int step = Math.max(1, Math.min(width, height) / 100);
        
        for (int y = 0; y < height; y += step) {
            for (int x = 0; x < width; x += step) {
                int rgb = image.getRGB(x, y);
                int a = (rgb >> 24) & 0xFF;
                
                if (a > 128) {
                    sumR += (rgb >> 16) & 0xFF;
                    sumG += (rgb >> 8) & 0xFF;
                    sumB += rgb & 0xFF;
                    pixelCount++;
                }
            }
        }
        
        if (pixelCount == 0) {
            return new ColorModel(128, 128, 128);
        }
        
        return new ColorModel(
                (int) (sumR / pixelCount),
                (int) (sumG / pixelCount),
                (int) (sumB / pixelCount)
        );
    }
}
