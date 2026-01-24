package java;
import java.util.Scanner;

public class HelloWorld {
    
    public static String greet(String name) {
        return "Hello, " + name + "! Welcome to Java.";
    }
    
    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("Welcome to Hello World Application");
        System.out.println("========================================");
        
        Scanner scanner = new Scanner(System.in);
        System.out.print("What is your name? ");
        String name = scanner.nextLine();
        
        String message = greet(name);
        System.out.println(message);
        System.out.println("========================================");
        
        scanner.close();
    }
}
