#include <FnAttribute/FnAttribute.h>
#include <FnAttribute/FnDataBuilder.h>
#include <FnAttribute/FnGroupBuilder.h>
#include <FnGeolib/op/FnGeolibOp.h>
#include <FnGeolib/util/Path.h>
#include <FnGeolibServices/FnGeolibCookInterfaceUtilsService.h>
#include <FnGeolibServices/FnResolutionTable.h>
#include <FnGeolibServices/FnXFormUtil.h>
#include <FnPluginSystem/FnPlugin.h>


namespace {

class PassRays : public Foundry::Katana::GeolibOp
{
	public:
		static void setup(Foundry::Katana::GeolibSetupInterface& interface);
		static void cook(Foundry::Katana::GeolibCookInterface& interface);
	private:
		static void setPassRays(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation);
		static void setDlPassRays(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation,
			bool& canMatchChildren);
		static void setPRManPassRays(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation,
			bool& canMatchChildren);
		static void setArnoldPassRays(Foundry::Katana::GeolibCookInterface& interface,
    		const std::string& activePassLocation,
			bool& canMatchChildren);
		static bool isCurrentRenderer(Foundry::Katana::GeolibCookInterface& interface,
			const std::string& rendererToTest);
		static const std::string getEnvVar(const std::string& envVarName,
			const std::string& defaultValue = "");
};


DEFINE_GEOLIBOP_PLUGIN(PassRays)

} // Katana anonymous namespace.

void registerPlugins()
{
    REGISTER_PLUGIN(PassRays, "PassRays", 0, 1);
}