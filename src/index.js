const system = require('system-commands');
system('ls').then(output => {
    console.log(output)
}).catch(error => {
    console.error(error)
})
