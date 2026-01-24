const readline = require('readline');

function greet(name) {
    return `Hello, ${name}! Welcome to JavaScript.`;
}

function main() {
    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });
    
    console.log('========================================');
    console.log('Welcome to Hello World Application');
    console.log('========================================');
    
    rl.question('What is your name? ', (name) => {
        const message = greet(name);
        console.log(message);
        console.log('========================================');
        rl.close();
    });
}

main();
