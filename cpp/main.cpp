#include <iostream>
#include <fstream>
#include <iomanip>
#include <string>

class RenderEngine
{public:
    void writePixel(int index, uint8_t pixel[4])
    {
        framebuffer.seekp(index);
        framebuffer.write(reinterpret_cast<char*>(pixel), 4);
    };

    void writeBuffer(uint8_t pixels[])
    {
        framebuffer.seekp(0, std::ios_base::beg);
        framebuffer.write(reinterpret_cast<char*>(pixels),TOTAL_PIXELS*4);
    };

    int getWidth()
    {
        return WIDTH;
    };

    int getHeigth()
    {
        return HEIGHT;
    };

    int getTotalPixels()
    {
        return TOTAL_PIXELS;
    };

    RenderEngine()
    {
        initFramebuffer();
        initScreenSize();
    };

private:
    std::fstream framebuffer;
    const char* FRAMEBUFFER_PATH = "/dev/fb0";
    uint16_t WIDTH, HEIGHT;
    uint32_t TOTAL_PIXELS;
    const uint8_t BYTES_PER_PIXEL = 4;

    void initFramebuffer()
    {
        framebuffer.open(FRAMEBUFFER_PATH, std::ios::in | std::ios::out);
        if (!framebuffer.is_open())
        {
            std::cerr << "Error opening /dev/fb0" << std::endl;
            exit(1);
        };
    };

    void initScreenSize()
    {
        std::fstream SYS_SIZE_FILE("/sys/class/graphics/fb0/virtual_size");
        if (!SYS_SIZE_FILE.is_open())
        {
            std::cerr << "Error opening /sys/class/graphics/fb0/virtual_size" << std::endl;
            exit(1);
        };
        std::string contents;
        std::getline(SYS_SIZE_FILE, contents);
        char comma;
        std::istringstream iss(contents);
        iss >> this->WIDTH >> comma >> this->HEIGHT;
        SYS_SIZE_FILE.close();
        TOTAL_PIXELS = WIDTH * HEIGHT;
    };
};

int main()
{
    RenderEngine renderEngine;
    int index = 0;
    uint8_t pixel[4] = {0,0,255,0};

    uint8_t localbuffer[renderEngine.getTotalPixels() * 4];

    for (int i = 0; i < renderEngine.getHeigth(); i++)
    {
        for (int o = 0; o < renderEngine.getWidth(); o++)
        {
            localbuffer[index]   = pixel[0];
            localbuffer[index+1] = pixel[1];
            localbuffer[index+2] = pixel[2];
            localbuffer[index+3] = pixel[3];
            index+=4;
        };
    };

    renderEngine.writeBuffer(localbuffer);

    return 0;
};